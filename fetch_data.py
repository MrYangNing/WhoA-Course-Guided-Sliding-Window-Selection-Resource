"""Fetch the public annotations; verifies the snapshot used in the manuscript."""
from pathlib import Path
from urllib.request import urlopen
import hashlib
url='https://raw.githubusercontent.com/linyueqian/SPIRAL_Dataset/master/data.jsonl'
expected='485225b9ef52c98298ceb06745c7acf022dcc7c6436c610a17dbd11e8022519f'
payload=urlopen(url,timeout=90).read()
digest=hashlib.sha256(payload).hexdigest()
if digest!=expected:raise RuntimeError(f'Upstream snapshot changed: {digest}. Review before overwriting.')
path=Path(__file__).resolve().parent/'data/spiral_data.jsonl';path.parent.mkdir(exist_ok=True)
path.write_bytes(payload)
print(path,len(payload),digest)
