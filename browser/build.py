from pathlib import Path
import hashlib,json
p=Path(__file__).parent
(p/'dist').mkdir(exist_ok=True)
(p/'validation').mkdir(exist_ok=True)
text=(p/'src/template.html').read_text(encoding='utf-8').replace('/*CORE*/',(p/'src/core.js').read_text(encoding='utf-8')).replace('/*UI*/',(p/'src/ui.js').read_text(encoding='utf-8'))
out=p/'dist/Nexus_Imaging_Studio_Browser_v1.html';out.write_text(text, encoding='utf-8', newline='\n')
b=out.read_bytes();assert len(b)<20_000_000
(p/'validation/artifact.json').write_text(json.dumps({'file':out.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'native_version':'3.2.13','browser_version':'1.0','native_payload_modified':False},indent=2)+'\n', encoding='utf-8', newline='\n')
print(len(b),hashlib.sha256(b).hexdigest())
