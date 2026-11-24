#!/usr/bin/env python3
"""
Truncated ZIP scanner / recoverer.

The external archives in external_datasets/ were only partially downloaded
(no End-Of-Central-Directory record), so zipfile.ZipFile() cannot open them.
This script locates every *local file header* by signature search and lists
(and optionally extracts) every member whose data is fully present on disk.
It handles members written with a trailing data descriptor (flag bit 3),
which is how SWEC-ETHZ and the Kaggle archive were packed.

Usage:
    python ssl/scan_truncated_zip.py <zip_path>                 # list only
    python ssl/scan_truncated_zip.py <zip_path> --extract <dir> [--pattern .mat] [--limit N]
"""
import os
import mmap
import struct
import zlib
import argparse

LFH_SIG = b'PK\x03\x04'
DD_SIG = b'PK\x07\x08'


def _find_headers(m):
    """Return list of (offset, name, flags, method, header_len) for plausible local headers."""
    out, i = [], 0
    while True:
        i = m.find(LFH_SIG, i)
        if i < 0 or i + 30 > len(m):
            break
        flags, method = struct.unpack('<HH', m[i + 6:i + 10])
        nlen, xlen = struct.unpack('<HH', m[i + 26:i + 30])
        raw_name = m[i + 30:i + 30 + nlen]
        try:
            name = raw_name.decode('utf-8')
            ok = 0 < nlen < 256 and name.isprintable() and method in (0, 8)
        except UnicodeDecodeError:
            ok = False
        if ok:
            out.append((i, name, flags, method, 30 + nlen + xlen))
        i += 4
    return out


def _decode(method, raw):
    if method == 0:
        return raw
    d = zlib.decompressobj(-15)
    return d.decompress(raw) + d.flush()


def scan(zip_path, extract_dir=None, pattern=None, limit=None):
    f = open(zip_path, 'rb')
    m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    headers = _find_headers(m)
    members, n_extracted = [], 0

    for k, (off, name, flags, method, hlen) in enumerate(headers):
        data_start = off + hlen
        is_last = (k == len(headers) - 1)
        if name.endswith('/'):
            members.append(dict(name=name, complete=True, size=0, data=None))
            continue
        if is_last:
            # Nothing after it -> truncated (archive was cut mid-member).
            members.append(dict(name=name, complete=False, size=len(m) - data_start))
            break

        next_off = headers[k + 1][0]
        # Strip data descriptor (optional signature + crc + sizes; 12/16/20/24 bytes).
        crc = None
        data_end = next_off
        if flags & 0x08:
            for dd_len in (24, 20, 16, 12):
                cand = next_off - dd_len
                if m[cand:cand + 4] == DD_SIG:
                    crc = struct.unpack('<I', m[cand + 4:cand + 8])[0]
                    data_end = cand
                    break
        else:
            crc = struct.unpack('<I', m[off + 14:off + 18])[0]

        members.append(dict(name=name, complete=True, size=data_end - data_start))

        if (extract_dir and (pattern is None or pattern in name)
                and (limit is None or n_extracted < limit)):
            out_path = os.path.join(extract_dir, name)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            if os.path.exists(out_path):
                n_extracted += 1
                continue
            data = _decode(method, m[data_start:data_end])
            if crc is not None and (zlib.crc32(data) & 0xFFFFFFFF) != crc:
                print(f"[warn] CRC mismatch, skipped: {name}")
                continue
            with open(out_path, 'wb') as g:
                g.write(data)
            n_extracted += 1
            print(f"[ok] {name} ({len(data)/1e6:.1f} MB, CRC verified={crc is not None})")
    return members, len(m)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('zip_path')
    ap.add_argument('--extract', default=None)
    ap.add_argument('--pattern', default=None)
    ap.add_argument('--limit', type=int, default=None)
    args = ap.parse_args()

    members, fsize = scan(args.zip_path, args.extract, args.pattern, args.limit)
    files = [x for x in members if not x['name'].endswith('/')]
    complete = [x for x in files if x['complete']]
    print(f"\nArchive bytes on disk : {fsize/1e9:.2f} GB")
    print(f"Complete file members : {len(complete)}")
    for x in complete[:15]:
        print(f"  {x['name']}  ({x['size']/1e6:.1f} MB stored)")
    if len(complete) > 15:
        print(f"  ... (+{len(complete)-15} more)")
    if files and not files[-1]['complete']:
        print(f"Truncated member      : {files[-1]['name']}")


if __name__ == '__main__':
    main()
