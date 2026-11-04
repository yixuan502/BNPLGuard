"""Explicit, default-deny release packaging; no training or remote publication."""
import argparse,json,re,shutil
from pathlib import Path
from .common import ROOT,read_json,write_json,sha256

POLICY='deployment/runtime_files.json'
SENSITIVE=[r'sk-[A-Za-z0-9_-]{30,}',r'ghp_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']


def release_files(root=ROOT):
    return json.loads((root/POLICY).read_text())['files']


def audit(root=ROOT):
    files=release_files(root);assert len(files)==len(set(files));total=0
    for name in files:
        p=Path(name)
        assert not p.is_absolute() and '..' not in p.parts,name
        assert not any(part in {'.venv','.env','__pycache__','.git','sources','node_modules'} for part in p.parts),name
        assert not name.startswith(('data/raw/','user_testing_records/','outputs/predictions/')),name
        assert not name.endswith(('.ipynb','.pdf','.zip','.env','secrets.toml')),name
        assert not any(x in p.name for x in ['test_predictions','validation_predictions','bootstrap_draws','bootstrap_indices']),name
        cursor=root
        for part in p.parts:
            assert part in {x.name for x in cursor.iterdir()},'Case-sensitive missing path: '+name
            cursor=cursor/part
        assert cursor.is_file() and not cursor.is_symlink(),name
        total+=cursor.stat().st_size
        if cursor.suffix in {'.py','.json','.toml','.md','.txt','.yml','.yaml','.lock'} or cursor.name=='.gitignore':
            text=cursor.read_text()
            assert not any(re.search(pattern,text) for pattern in SENSITIVE),'Potential credential in '+name
    freeze=json.loads((root/'config/stage5_frozen.json').read_text())
    assert sha256(root/freeze['artifact'])==freeze['artifact_sha256']
    assert sha256(root/'config/feature_schema.json')==freeze['schema_sha256']
    assert sha256(root/'data/splits/cfpb_split_ids.json')==freeze['split_sha256']
    return {'file_count':len(files),'bytes':total,'secrets_scan':'No known credential formats found; explicit allowlist reviewed','case_sensitive_paths':'PASS','files_sha256':{name:sha256(root/name) for name in files}}


def build(output):
    receipt=audit();out=Path(output)
    if not out.is_absolute():out=ROOT/out
    if out.exists():raise FileExistsError('Preserve existing clean tree; choose a new output directory')
    out.mkdir(parents=True)
    for name in release_files():
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    assert audit(out)['files_sha256']==receipt['files_sha256']
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['audit','build']);p.add_argument('--output',default='deployment/clean_tree_v1');a=p.parse_args()
    r=build(a.output) if a.action=='build' else audit();write_json('outputs/deploy/stage8_v1/package_manifest.json',r)
    print(json.dumps({k:v for k,v in r.items() if k!='files_sha256'},indent=2))
