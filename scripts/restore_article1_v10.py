"""Verify and restore V10 checkpoints from the repository's raw archives."""
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]


def checked(path,expected):
    payload=path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=expected:raise RuntimeError(f'Checksum mismatch: {path}')
    return payload


def restore(root=ROOT):
    root=Path(root).resolve()
    manifest=json.loads((root/'outputs/campaign_archives/V10_RAW_ARCHIVES.json').read_text())
    for item in manifest:
        archive=root/item['path']
        if 'parts' in item:
            payload=b''.join(checked(root/p['path'],p['sha256']) for p in item['parts'])
            if hashlib.sha256(payload).hexdigest()!=item['sha256']:raise RuntimeError('Assembled checksum mismatch')
            if archive.exists():checked(archive,item['sha256'])
            else:archive.write_bytes(payload)
        checked(archive,item['sha256'])
        with tarfile.open(archive,'r:gz') as tar:
            members=tar.getmembers()
            if len(members)!=item['files']:raise RuntimeError('Archive member count mismatch')
            for member in members:
                target=(root/member.name).resolve()
                if not member.isfile() or not target.is_relative_to(root):raise RuntimeError('Unsafe archive member')
                data=tar.extractfile(member).read()
                if target.exists():
                    if target.read_bytes()!=data:raise RuntimeError(f'Existing file differs; preserved: {target}')
                else:
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        print(f"Verified and restored {item['suite']}: {item['final_checkpoints']} final models")


if __name__=='__main__':restore()
