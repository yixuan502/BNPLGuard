"""Optional public-source refresh. Never executes fetched code or requests a CSV."""
import json,urllib.request,urllib.error,hashlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Fetch public metadata/Notebook evidence only; never download CSV.')
parser.add_argument('--output-dir',required=True)
args=parser.parse_args()
root=ROOT/args.output_dir
if root.exists():raise FileExistsError(root)
root.mkdir(parents=True)
urls={
'dataset_metadata':'https://www.kaggle.com/api/v1/datasets/view/shree0910/buy-now-and-pay-later-fintech-ml-dataset',
'notebook_source':'https://www.kaggle.com/api/v1/kernels/pull/sumedh1507/bnpl-credit-risk-insights',
'dataset_page':'https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset',
'notebook_page':'https://www.kaggle.com/code/sumedh1507/bnpl-credit-risk-insights'}
records=[]
for name,url in urls.items():
 target=root/(name+'.txt')
 if target.exists():raise FileExistsError(target)
 record={'name':name,'url':url,'accessed_at':datetime.now(ZoneInfo('Australia/Sydney')).isoformat()}
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=25) as response:
   data=response.read(20_000_001)
   if len(data)>20_000_000:raise ValueError('Response exceeds source-inspection size limit')
   record.update(status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
   target.write_bytes(data);record['saved_file']=str(target.relative_to(root.parent))
 except Exception as error:
  record['error']=str(error)
 records.append(record)
 print(name, {k:v for k,v in record.items() if k in ['status','content_type','bytes','error']},flush=True)
(root/'access_log.json').write_text(json.dumps(records,indent=2)+'\n')
