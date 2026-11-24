#!/usr/bin/env python3
"""
SimCLR Pretraining on the 16-patient SWEC Short-term Dataset (752,572 windows).
"""
import os
import time
import argparse
import numpy as np
import pandas as pd
import torch

import ssl_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
MODELS = os.path.join(HERE, 'models')

def batches(arr, bs, shuffle, rng):
    idx = rng.permutation(len(arr)) if shuffle else np.arange(len(arr))
    for i in range(0, len(idx) - bs + 1, bs):
        yield torch.from_numpy(arr[idx[i:i + bs]].astype(np.float32))

@torch.no_grad()
def evaluate(model, arr, bs, dev):
    model.eval()
    rng = np.random.default_rng(0)
    torch.manual_seed(0)
    L, A, n = 0.0, 0.0, 0
    # Evaluate on a subset of 10,000 validation windows for speed
    sub_val = arr[:min(10000, len(arr))]
    for xb in batches(sub_val, bs, False, rng):
        xb = xb.to(dev)
        loss, acc = C.nt_xent(model(C.augment(xb)), model(C.augment(xb)))
        L += loss.item(); A += acc.item(); n += 1
    return L / max(n, 1), A / max(n, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=15)
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--tau', type=float, default=0.2)
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    os.makedirs(MODELS, exist_ok=True)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    dev = C.get_device()

    corpus_path = os.path.join(DATA, 'swec_shortterm_pretrain.npy')
    if not os.path.exists(corpus_path):
        print(f"[ERROR] {corpus_path} not found.")
        return

    full_arr = np.load(corpus_path)
    print(f"Loaded Short-term SWEC corpus: {full_arr.shape}")

    # 90% Train / 10% Val split
    n_samples = len(full_arr)
    n_val = int(0.1 * n_samples)
    perm = rng.permutation(n_samples)
    val_idx = perm[:n_val]
    train_idx = perm[n_val:]

    tr = full_arr[train_idx]
    va = full_arr[val_idx]

    print(f"Device: {dev} | Train windows: {len(tr)} | Val windows: {len(va)}")

    model = C.SimCLR().to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    steps = args.epochs * (len(tr) // args.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=steps, pct_start=0.1)

    v0 = evaluate(model, va, args.batch, dev)
    log = [dict(epoch=0, train_loss=np.nan, train_acc=np.nan, val_loss=v0[0], val_acc=v0[1])]
    print(f"[Epoch 0] Val Loss: {v0[0]:.4f} | Val Acc: {v0[1]:.3f}")

    best = np.inf
    out_model_path = os.path.join(MODELS, 'ssl_encoder_shortterm.pt')

    for ep in range(1, args.epochs + 1):
        model.train()
        t0, L, A, n = time.time(), 0.0, 0.0, 0
        for xb in batches(tr, args.batch, True, rng):
            xb = xb.to(dev)
            loss, acc = C.nt_xent(model(C.augment(xb)), model(C.augment(xb)), args.tau)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
            L += loss.item()
            A += acc.item()
            n += 1
        
        vl, vacc = evaluate(model, va, args.batch, dev)
        log.append(dict(epoch=ep, train_loss=L / n, train_acc=A / n, val_loss=vl, val_acc=vacc))
        print(f"[Epoch {ep}/{args.epochs}] Train Loss: {L/n:.4f} Acc: {A/n:.3f} | Val Loss: {vl:.4f} Acc: {vacc:.3f} ({time.time()-t0:.1f}s)", flush=True)

        if vl < best:
            best = vl
            torch.save(model.encoder.state_dict(), out_model_path)
            
        pd.DataFrame(log).to_csv(os.path.join(MODELS, 'pretrain_shortterm_log.csv'), index=False)

    print(f"\n[Completed] Best Val Loss: {best:.4f}. Model saved to {out_model_path}")

if __name__ == '__main__':
    main()
