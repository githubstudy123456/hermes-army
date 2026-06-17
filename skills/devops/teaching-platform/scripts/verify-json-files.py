#!/usr/bin/env python3
"""Verify JSON content files for syntax validity and content completeness."""

import json
import os
import sys

data_dir = '/home/ubuntu/teaching-platform/data/物理/'

def verify_file(path):
    """Verify a single JSON file. Returns (ok, messages)."""
    msgs = []
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON INVALID: {e}"]

    if isinstance(data, list):
        # New flat array format
        items = data
        for item in items:
            content = str(item.get('content', ''))
            if len(content) < 50:
                msgs.append(f"  [{item.get('id','?')}] content too short ({len(content)} chars)")
            # Check for unescaped quotes
            if '"' in content:
                msgs.append(f"  [{item.get('id','?')}] contains unescaped ASCII quote in content")
    elif isinstance(data, dict):
        # Old format - check if知识点 content is empty
        kps = data.get('知识点', [])
        for kp in kps:
           讲解 = kp.get('讲解', '')
            if not 讲解 or len(str(讲解)) < 10:
                msgs.append(f"  stub: 知识点 '{kp.get('title','')}' has empty 讲解")
    else:
        msgs.append(f"  Unknown format type: {type(data)}")

    return len(msgs) == 0, msgs

def main():
    files_checked = 0
    files_with_issues = 0
    stub_files = []

    for fname in sorted(os.listdir(data_dir)):
        if not fname.endswith('.json') or fname in ('index.json', 'stars.json'):
            continue
        path = os.path.join(data_dir, fname)
        ok, msgs = verify_file(path)
        files_checked += 1
        if not ok:
            files_with_issues += 1
            print(f"\n{fname}:")
            for m in msgs:
                print(m)
            # Also detect stub files
            try:
                with open(path) as f:
                    data = json.load(f)
                if isinstance(data, dict) and '知识点' in data:
                    stub = all(
                        not kp.get('讲解') or len(str(kp.get('讲解',''))) < 10
                        for kp in data.get('知识点', [])
                    )
                    if stub:
                        stub_files.append(fname)
            except:
                pass

    print(f"\n{'='*50}")
    print(f"Files checked: {files_checked}")
    print(f"Files with issues: {files_with_issues}")
    if stub_files:
        print(f"Stub files (old format, empty讲解): {len(stub_files)}")
        for f in stub_files[:10]:
            print(f"  {f}")
        if len(stub_files) > 10:
            print(f"  ... and {len(stub_files)-10} more")

if __name__ == '__main__':
    main()