#!/usr/bin/env python3
"""Read-only archival verifier, regenerated after recovery of a truncated bundle.

The unavailable original reconstruction script is not reproduced by this file.
See RECOVERY_NOTICE.md. This replacement supports the documented verify command.
It neither trains models nor writes Git history.
"""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def verify(repo):
    stages = ("V06", "V07", "V08", "V09")
    rows = list(csv.DictReader(io.StringIO(
        git(repo, "show", "archive/v09:INVENTORY.csv").decode("utf-8")
    )))
    kept = [r for r in rows if r["status"].startswith("preserved")]
    cache = {}
    counts = {}
    proc = subprocess.Popen(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    try:
        for stage_index, stage in enumerate(stages):
            ref = "archive/" + stage.lower()
            tree = {}
            for entry in git(repo, "ls-tree", "-r", "-z", ref).split(b"\0"):
                if not entry:
                    continue
                meta, path = entry.split(b"\t", 1)
                mode, kind, sha = meta.split()
                if kind != b"blob" or mode not in (b"100644", b"100755"):
                    raise ValueError("Unsupported inventory entry: " + repr(path))
                tree[path.decode("utf-8")] = sha
            checked = 0
            for row in kept:
                introduced = stages.index(row["introduction_version"])
                path = row["repository_path"]
                if introduced > stage_index:
                    if path in tree:
                        raise ValueError(f"{stage}: premature introduction: {path}")
                    continue
                if path not in tree:
                    raise ValueError(f"{stage}: missing file: {path}")
                sha = tree[path]
                if sha not in cache:
                    proc.stdin.write(sha + b"\n")
                    proc.stdin.flush()
                    header = proc.stdout.readline().split()
                    if len(header) != 3 or header[1] != b"blob":
                        raise ValueError("Missing or invalid Git blob: " + repr(header))
                    size = int(header[2])
                    data = proc.stdout.read(size)
                    if len(data) != size or proc.stdout.read(1) != b"\n":
                        raise ValueError("Truncated Git blob")
                    cache[sha] = (size, hashlib.sha256(data).hexdigest())
                if cache[sha] != (int(row["size_bytes"]), row["sha256"]):
                    raise ValueError(f"{stage}: size or SHA-256 mismatch: {path}")
                checked += 1
            counts[stage] = checked
    finally:
        proc.stdin.close()
        proc.stdout.close()
        proc.wait()
    if proc.returncode:
        raise RuntimeError("git cat-file failed")
    refs = {stage: git(repo, "rev-parse", "archive/" + stage.lower()).decode().strip()
            for stage in stages}
    for previous, current in zip(stages, stages[1:]):
        parent = git(repo, "rev-parse", refs[current] + "^").decode().strip()
        if parent != refs[previous]:
            raise ValueError(f"Unexpected parent for {current}")
    expected_base = "59498a9fde0662dabc0c407300b4d6c89f40f64f"
    if git(repo, "rev-parse", refs["V06"] + "^").decode().strip() != expected_base:
        raise ValueError("Original initial commit not preserved")
    for tag, stage in (("v0.7.0", "V07"), ("article1-v0.8", "V08"),
                       ("article1-v0.9", "V09")):
        if git(repo, "rev-parse", tag + "^{commit}").decode().strip() != refs[stage]:
            raise ValueError("Incorrect tag: " + tag)
    if git(repo, "rev-parse", "main").decode().strip() != refs["V09"]:
        raise ValueError("main does not point to V09")
    subprocess.run(["git", "-C", str(repo), "fsck", "--full"], check=True)
    print(json.dumps({"status": "verified", "preserved_files": len(kept),
                      "checked_files_by_stage": counts, "commits": refs}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify"])
    parser.add_argument("--repo", type=Path, default=Path("."))
    args = parser.parse_args()
    verify(args.repo.resolve())
