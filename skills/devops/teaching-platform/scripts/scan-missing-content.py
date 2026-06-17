#!/usr/bin/env python3
"""Scan teaching platform data dirs for missing content files."""
import json, os, sys

def scan_subject(subject_dir):
    """Return (existing_count, total_count, missing_list) for a subject directory."""
    index_path = os.path.join(subject_dir, 'index.json')
    if not os.path.exists(index_path):
        return None

    with open(index_path) as f:
        index = json.load(f)

    existing = set(
        f.replace('.json', '')
        for f in os.listdir(subject_dir)
        if f.endswith('.json') and f not in ['index.json', 'stars.json']
    )

    total = sum(len(ch['知识点']) for ch in index['章节'])
    missing = []
    for ch in index['章节']:
        for kp in ch['知识点']:
            if kp['id'] not in existing:
                missing.append((kp['id'], kp['name']))

    return len(existing), total, missing

if __name__ == '__main__':
    base = '/home/ubuntu/teaching-platform/data/'
    for subject in sorted(os.listdir(base)):
        subject_dir = os.path.join(base, subject)
        if os.path.isdir(subject_dir):
            result = scan_subject(subject_dir)
            if result:
                existing, total, missing = result
                status = '✓' if not missing else f"MISSING {len(missing)}"
                print(f"{subject}: {existing}/{total} {status}")
                if missing:
                    for mid, mname in missing[:5]:
                        print(f"  - {mid}: {mname}")
                    if len(missing) > 5:
                        print(f"  ... and {len(missing)-5} more")
            else:
                print(f"{subject}: no index.json")