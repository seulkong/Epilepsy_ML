#!/usr/bin/env python3
"""
Step 2 - Self-supervised contrastive pretraining (SimCLR) on external SWEC-ETHZ iEEG.

Inputs : ssl/data/swec_pretrain_{train,val}.npy
Outputs: ssl/models/ssl_encoder.pt          (pretrained encoder weights)
         ssl/models/random_encoder.pt       (same architecture, untrained; control)
         ssl/models/pretrain_log.csv        (per-epoch train/val NT-Xent loss + top-1 acc)

Validation metric: contrastive loss / positive-pair retrieval accuracy on the
held-out SWEC hour. It only monitors SSL convergence; no outcome labels are used.
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
    for i in range(0, len(idx) - bs + 1, bs):  # drop last for stable contrastive batch
        yield torch.from_numpy(arr[idx[i:i + bs]].astype(np.float32))


@torch.no_grad()
def evaluate(model, arr, bs, dev):
    model.eval()
    rng = np.random.default_rng(0)
    torch.manual_seed(0)
    L, A, n = 0.0, 0.0, 0
    for xb in batches(arr, bs, False, rng):
        xb = xb.to(dev)
        loss, acc = C.nt_xent(model(C.augment(xb)), model(C.augment(xb)))
        L += loss.item(); A += acc.item(); n += 1
    return L / max(n, 1), A / max(n, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--epochs', type=int, default=30)
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--tau', type=float, default=0.2)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--max_train', type=int, default=None, help='subsample for quick tests')
    args = ap.parse_args()

    os.makedirs(MODELS, exist_ok=True)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    dev = C.get_device()

    tr = np.load(os.path.join(DATA, 'swec_pretrain_train.npy'))
    va = np.load(os.path.join(DATA, 'swec_pretrain_val.npy'))
    if args.max_train:
        tr = tr[rng.choice(len(tr), min(args.max_train, len(tr)), replace=False)]
    print(f"device={dev}  train={tr.shape}  val={va.shape}")

    model = C.SimCLR().to(dev)
    # Save the untrained (random-init) encoder as a control for the downstream analysis
    torch.save(model.encoder.state_dict(), os.path.join(MODELS, 'random_encoder.pt'))

    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    steps = args.epochs * (len(tr) // args.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=steps, pct_start=0.1)

    v0 = evaluate(model, va, args.batch, dev)
    log = [dict(epoch=0, train_loss=np.nan, train_acc=np.nan, val_loss=v0[0], val_acc=v0[1])]
    print(f"[epoch 0] val_loss={v0[0]:.4f} val_acc={v0[1]:.3f}")
    best = np.inf
    for ep in range(1, args.epochs + 1):
        model.train()
        t0, L, A, n = time.time(), 0.0, 0.0, 0
        for xb in batches(tr, args.batch, True, rng):
            xb = xb.to(dev)
            loss, acc = C.nt_xent(model(C.augment(xb)), model(C.augment(xb)), args.tau)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step(); sched.step()
            L += loss.item(); A += acc.item(); n += 1
        vl, vacc = evaluate(model, va, args.batch, dev)
        log.append(dict(epoch=ep, train_loss=L / n, train_acc=A / n, val_loss=vl, val_acc=vacc))
        print(f"[epoch {ep}] train_loss={L/n:.4f} acc={A/n:.3f} | val_loss={vl:.4f} acc={vacc:.3f} "
              f"({time.time()-t0:.0f}s)", flush=True)
        if vl < best:
            best = vl
            torch.save(model.encoder.state_dict(), os.path.join(MODELS, 'ssl_encoder.pt'))
        pd.DataFrame(log).to_csv(os.path.join(MODELS, 'pretrain_log.csv'), index=False)

    print(f"done. best val_loss={best:.4f}; encoder saved to {MODELS}/ssl_encoder.pt")


if __name__ == '__main__':
    main()
