"""Local-only, version-isolated Nexus installer. No downloads or dependency changes."""
from pathlib import Path, PurePosixPath
import contextlib,argparse,hashlib,io,json,os,re,shutil,stat,subprocess,sys,tempfile,webbrowser,zipfile
MANIFEST_SHA = 'a5b5e636d7025cfc194ac69682499f94d9ba80235b79a6a6a7a85ebee5cc7b16'
ROOT=Path(__file__).resolve().parent

def digest(b):return hashlib.sha256(b).hexdigest()
def load():
 raw=(ROOT/'package_manifest.json').read_bytes()
 if digest(raw)!=MANIFEST_SHA:raise ValueError('Package manifest checksum mismatch')
 return json.loads(raw)
def safe_name(name):
 p=PurePosixPath(name)
 if not name or '\\' in name or ':' in name or p.is_absolute() or '..' in p.parts or str(p)!=name:raise ValueError('Unsafe archive path')
 for part in p.parts:
  stem=part.split('.')[0].upper()
  if part.endswith((' ','.')) or any(ord(c)<32 or c in '<>"|?*' for c in part) or stem in {'CON','PRN','AUX','NUL','CONIN$','CONOUT$',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}:raise ValueError('Unsafe Windows archive name')
 return p

@contextlib.contextmanager
def installation_lock(path):
 try:path.mkdir()
 except FileExistsError:raise RuntimeError("Another installation is in progress, or a previous install was interrupted. Confirm no installer is running before removing this lock: "+str(path))
 try:yield
 finally:path.rmdir()

def unpack(manifest,destination):
 for key in ('product_id','version'):
  value=manifest.get(key)
  if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}',value):raise ValueError('Invalid package identity')
  safe_name(value)
 entry=manifest.get('entrypoint');safe_name(entry)
 if entry not in manifest.get('files',{}):raise ValueError('Entrypoint not in file inventory')
 if not re.fullmatch(r'[0-9a-f]{64}',manifest.get('payload_sha256','')):raise ValueError('Invalid payload digest')
 pieces=[]
 for part in manifest['parts']:
  name=part['name'];safe_name(name)
  if '/' in name:raise ValueError('Unsafe part name')
  data=(ROOT/name).read_bytes()
  if len(data)!=part['bytes'] or digest(data)!=part['sha256']:raise ValueError('Missing or damaged data part: '+name)
  pieces.append(data)
 data=b''.join(pieces)
 if digest(data)!=manifest['payload_sha256']:raise ValueError('Payload checksum mismatch')
 destination=Path(destination).expanduser().resolve();destination.mkdir(parents=True,exist_ok=True)
 final=destination/(manifest['product_id']+'-'+manifest['version']+'-'+manifest['payload_sha256'][:12])
 # Never replace an existing directory or alter its documents/state.
 if final.exists():raise FileExistsError('This version already exists. Open its existing launcher, or choose a new installation folder: '+str(final))
 expected=manifest['files']
 with installation_lock(destination/(final.name+'.install-lock')), tempfile.TemporaryDirectory(prefix='.nexus-stage-',dir=destination) as tmp:
  stage=Path(tmp)/'app';stage.mkdir()
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   entries=z.infolist()
   if len(entries)!=len(expected) or {i.filename for i in entries}!=set(expected):raise ValueError('Archive file inventory mismatch')
   seen=set()
   for i in entries:
    safe_name(i.filename)
    key=i.filename.casefold()
    if key in seen or i.is_dir() or stat.S_ISLNK(i.external_attr>>16):raise ValueError('Duplicate or unsupported archive entry')
    seen.add(key);rec=expected[i.filename]
    if i.file_size!=rec['bytes']:raise ValueError('File size mismatch')
    content=z.read(i)
    if digest(content)!=rec['sha256']:raise ValueError('File checksum mismatch')
    p=stage/i.filename;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
   entry=stage/manifest['entrypoint']
   if not entry.is_file():raise ValueError('Missing launch entrypoint')
  # Target is version+hash scoped and must not have appeared during extraction.
  if final.exists():raise FileExistsError('Destination appeared during installation; preserved without replacement')
  stage.rename(final)
 return final

def launch(folder,m):
 entry=folder/m['entrypoint']
 if m['launch_kind']=='html':
  if not webbrowser.open(entry.as_uri()):raise RuntimeError('Browser did not accept launch; open '+str(entry))
 elif m['launch_kind']=='python':subprocess.Popen([sys.executable,str(entry)],cwd=folder)
 elif m['launch_kind']=='windows':
  if os.name!='nt':raise RuntimeError('Installed successfully. Launch this application on Windows: '+str(entry))
  os.startfile(str(entry))
 else:raise ValueError('Unsupported launch kind')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,default=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.local/share')))/'NexusReleases');p.add_argument('--no-launch',action='store_true');p.add_argument('--yes',action='store_true',help='Accept the printed local install plan');a=p.parse_args();m=load()
 print(m['product']+' '+m['version']);print('Install a new isolated version under: '+str(a.destination));print('No downloads, drivers, dependencies, PATH, registry or existing app/state changes. Existing Python/runtime dependencies must already be available.');print('Launch after installation: '+str(not a.no_launch))
 if not a.yes and input('Install? [y/N] ').strip().lower() not in ('y','yes'):return
 folder=unpack(m,a.destination);print('Installation complete (100%): '+str(folder))
 if not a.no_launch:launch(folder,m)
if __name__=='__main__':
 try:main()
 except Exception as e:print('Installation/launch error: '+str(e),file=sys.stderr);sys.exit(1)
