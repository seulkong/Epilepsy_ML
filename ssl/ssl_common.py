#!/usr/bin/env python3
"""
Shared components for the self-supervised (SSL) iEEG representation pipeline.

Design (to be described verbatim in the Methods section):
  * Input unit      : single-channel, 4-s window, resampled to 256 Hz (1024 samples)
  * Preprocessing   : 4th-order zero-phase Butterworth band-pass 1-100 Hz,
                      per-window z-score; windows with flat signal or |z|>20 rejected
  * Encoder         : 5-block 1D-CNN (channel-agnostic, so montages of any size work)
                      -> global average pooling -> 128-d embedding
  * Projection head : 128 -> 128 -> 64 (used only during pretraining, discarded after)
  * Objective       : SimCLR NT-Xent contrastive loss between two stochastic
                      augmentations of the same window
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.signal import butter, sosfiltfilt, resample_poly
from fractions import Fraction

TARGET_FS = 256
WIN_SEC = 4.0
WIN_LEN = int(TARGET_FS * WIN_SEC)  # 1024
BAND = (1.0, 100.0)
EMB_DIM = 128

_SOS = butter(4, BAND, btype='bandpass', fs=TARGET_FS, output='sos')


# ------------------------------------------------------------------------------
# Signal preprocessing
# ------------------------------------------------------------------------------
def resample_to_target(x, fs):
    """Resample (C, T) array from fs to TARGET_FS with polyphase filtering."""
    if abs(fs - TARGET_FS) < 1e-6:
        return x.astype(np.float32)
    frac = Fraction(TARGET_FS / fs).limit_denominator(1000)
    return resample_poly(x, frac.numerator, frac.denominator, axis=-1).astype(np.float32)


def bandpass(x):
    return sosfiltfilt(_SOS, x, axis=-1).astype(np.float32)


def make_windows(x, stride_sec=WIN_SEC, max_windows=None):
    """
    Cut (C, T) signal (already at TARGET_FS, filtered) into per-channel windows.
    Returns windows (N, WIN_LEN) z-scored, and channel index per window (N,).
    """
    C, T = x.shape
    stride = int(stride_sec * TARGET_FS)
    starts = np.arange(0, T - WIN_LEN + 1, stride)
    if max_windows is not None and len(starts) > max_windows:
        starts = starts[np.linspace(0, len(starts) - 1, max_windows).astype(int)]
    if len(starts) == 0:
        return np.empty((0, WIN_LEN), np.float32), np.empty((0,), int)
    idx = starts[:, None] + np.arange(WIN_LEN)[None, :]          # (S, L)
    w = x[:, idx]                                                # (C, S, L)
    ch = np.repeat(np.arange(C), len(starts))
    w = w.reshape(-1, WIN_LEN)
    mu = w.mean(axis=1, keepdims=True)
    sd = w.std(axis=1, keepdims=True)
    ok = (sd[:, 0] > 1e-8)
    w = (w - mu) / np.where(sd > 1e-8, sd, 1.0)
    ok &= (np.abs(w).max(axis=1) < 20.0)
    return w[ok].astype(np.float32), ch[ok]


# ------------------------------------------------------------------------------
# Model
# ------------------------------------------------------------------------------
def _block(cin, cout, k):
    return nn.Sequential(
        nn.Conv1d(cin, cout, k, stride=2, padding=k // 2, bias=False),
        nn.BatchNorm1d(cout),
        nn.GELU(),
    )


class Encoder(nn.Module):
    def __init__(self, emb_dim=EMB_DIM):
        super().__init__()
        self.net = nn.Sequential(
            _block(1, 32, 9),
            _block(32, 64, 7),
            _block(64, 128, 7),
            _block(128, 128, 5),
            _block(128, emb_dim, 3),
        )

    def forward(self, x):            # x: (B, L)
        h = self.net(x.unsqueeze(1))  # (B, D, L/32)
        return h.mean(dim=-1)         # (B, D)


class SimCLR(nn.Module):
    def __init__(self, emb_dim=EMB_DIM, proj_dim=64):
        super().__init__()
        self.encoder = Encoder(emb_dim)
        self.proj = nn.Sequential(nn.Linear(emb_dim, emb_dim), nn.GELU(), nn.Linear(emb_dim, proj_dim))

    def forward(self, x):
        return self.proj(self.encoder(x))


def nt_xent(z1, z2, tau=0.2):
    """SimCLR NT-Xent loss; also returns top-1 positive-pair retrieval accuracy."""
    z = F.normalize(torch.cat([z1, z2]), dim=1)
    n = z1.shape[0]
    sim = z @ z.t() / tau
    sim.fill_diagonal_(float('-inf'))
    target = torch.cat([torch.arange(n, 2 * n), torch.arange(0, n)]).to(z.device)
    loss = F.cross_entropy(sim, target)
    acc = (sim.argmax(dim=1) == target).float().mean()
    return loss, acc


# ------------------------------------------------------------------------------
# Augmentations (batched, on device)
# ------------------------------------------------------------------------------
def augment(x):
    """Stochastic iEEG augmentations applied independently per sample. x: (B, L)."""
    B, L = x.shape
    dev = x.device
    # 1) random circular time shift up to 0.5 s
    shifts = torch.randint(-TARGET_FS // 2, TARGET_FS // 2 + 1, (B,), device=dev)
    ar = torch.arange(L, device=dev)[None, :]
    x = torch.gather(x, 1, (ar - shifts[:, None]) % L)
    # 2) amplitude scaling and polarity flip
    scale = torch.empty(B, 1, device=dev).uniform_(0.8, 1.2)
    sign = torch.where(torch.rand(B, 1, device=dev) < 0.5, -1.0, 1.0)
    x = x * scale * sign
    # 3) additive Gaussian noise
    x = x + 0.1 * torch.randn_like(x)
    # 4) random time masking (10-20 % of the window)
    mlen = (torch.empty(B, device=dev).uniform_(0.1, 0.2) * L).long()
    mstart = (torch.rand(B, device=dev) * (L - mlen)).long()
    mask = (ar >= mstart[:, None]) & (ar < (mstart + mlen)[:, None])
    x = x.masked_fill(mask, 0.0)
    # 5) random band-stop (zero a 4-12 Hz wide band in the spectrum)
    Xf = torch.fft.rfft(x, dim=1)
    freqs = torch.fft.rfftfreq(L, d=1.0 / TARGET_FS).to(dev)[None, :]
    f0 = torch.empty(B, 1, device=dev).uniform_(BAND[0], BAND[1] - 12)
    bw = torch.empty(B, 1, device=dev).uniform_(4, 12)
    apply = (torch.rand(B, 1, device=dev) < 0.5)
    stop = (freqs >= f0) & (freqs <= f0 + bw) & apply
    Xf = Xf.masked_fill(stop, 0)
    return torch.fft.irfft(Xf, n=L, dim=1)


def get_device():
    if torch.backends.mps.is_available():
        return torch.device('mps')
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')
