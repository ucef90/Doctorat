"""Pack completed V10 raw runs without changing historical tracked outputs."""
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    output=ROOT/'outputs/campaign_archives';output.mkdir(exist_ok=True)
    inventory=[]
    for suite,expected in [('robustness',200),('budget',200),('common_loss',160)]:
        source=ROOT/f'outputs/{suite}_v10_campaign'
        completion=json.loads((source/'completion.json').read_text())
        if completion['completed']!=expected or completion['failed']!=0:
            raise RuntimeError(f'{suite}: incomplete campaign')
        files=sorted(p for p in source.rglob('*') if p.is_file())
        checkpoints=[p for p in files if p.name=='model.pt']
        if len(checkpoints)!=expected:raise RuntimeError('Missing final checkpoints')
        archive=output/f'{suite}_v10_raw.tar.gz'
        if archive.exists():raise FileExistsError(archive)
        with archive.open('wb') as raw:
            with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
                with tarfile.open(fileobj=zipped,mode='w|') as tar:
                    for p in files:
                        info=tar.gettarinfo(str(p),arcname=str(p.relative_to(ROOT)))
                        info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
                        with p.open('rb') as f:tar.addfile(info,f)
        with tarfile.open(archive,'r:gz') as tar:
            members=tar.getmembers()
            if len(members)!=len(files):raise RuntimeError('Archive inventory mismatch')
            for member,p in zip(members,files):
                if member.name!=str(p.relative_to(ROOT)):raise RuntimeError('Archive path mismatch')
                if hashlib.sha256(tar.extractfile(member).read()).digest()!=hashlib.sha256(p.read_bytes()).digest():
                    raise RuntimeError('Archive byte verification failed')
        inventory.append(dict(suite=suite,path=str(archive.relative_to(ROOT)),files=len(files),
            completed_trainings=expected,final_checkpoints=len(checkpoints),size_bytes=archive.stat().st_size,
            sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),verified_all_members=True))
        if archive.stat().st_size > 10_000_000:
            payload=archive.read_bytes();parts=[]
            for i,start in enumerate(range(0,len(payload),6_000_000),1):
                part=archive.with_name(archive.name+f'.part{i:02d}')
                part.write_bytes(payload[start:start+6_000_000])
                parts.append(dict(path=str(part.relative_to(ROOT)),size_bytes=part.stat().st_size,
                    sha256=hashlib.sha256(part.read_bytes()).hexdigest()))
            inventory[-1]['parts']=parts
        print(inventory[-1],flush=True)
    (output/'V10_RAW_ARCHIVES.json').write_text(json.dumps(inventory,indent=2))


if __name__=='__main__':main()
