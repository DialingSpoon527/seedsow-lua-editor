"""Publish the prepared source release using command-line Git authentication.

Run from a normal signed-in Windows terminal. Credentials stay in memory and
the configured Git credential helper; no token is printed or written here.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY = 'DialingSpoon527/seedsow-lua-editor'
REMOTE_URL = 'https://github.com/'+REPOSITORY+'.git'
from package_release import package


def release_assets(info):
    from package_save import starter_files
    source = Path(info['zip'])
    save = ROOT/'dist/Seedsow-Lua-Editor-Save.zip'
    if not save.is_file():
        raise RuntimeError('Prepare dist/Seedsow-Lua-Editor-Save.zip with maintainer/package_save.py first.')
    reviewed = starter_files(save)
    with zipfile.ZipFile(save) as archive:
        if set(archive.namelist())!=set(reviewed) or any(archive.read(n)!=b for n,b in reviewed.items()):
            raise RuntimeError('The save ZIP contains unreviewed files or bytes; it is not cleared for publication.')
    result = []
    for archive in (save,source):
        checksum = archive.with_suffix('.zip.sha256')
        manifest = archive.with_suffix('.manifest.json')
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if checksum.read_text().split()[0]!=digest or json.loads(manifest.read_text())['sha256']!=digest:
            raise RuntimeError('Asset checksum or manifest does not match '+archive.name)
        result.extend([(archive,'application/zip'),(checksum,'text/plain'),(manifest,'application/json')])
    return result


def git_executable():
    if os.name == 'nt':
        candidate = Path(os.environ.get('ProgramFiles',r'C:\Program Files'))/'Git/cmd/git.exe'
        if candidate.is_file():
            return str(candidate)
    candidate = shutil.which('git')
    if not candidate:
        raise RuntimeError('Install Git, then run this command again.')
    return candidate


def git(*args, capture=True, input_text=None):
    result = subprocess.run([git_executable(),'-C',str(ROOT),*args],
                            input=input_text,text=True,capture_output=capture)
    if result.returncode:
        raise RuntimeError((result.stderr or 'Git command failed.').strip())
    return result.stdout.strip() if capture else ''


def credential():
    # Keep credential stdout private, while allowing sign-in instructions on stderr.
    print('Checking GitHub sign-in. Complete any browser or sign-in window that opens.',flush=True)
    try:
        result = subprocess.run([git_executable(),'-C',str(ROOT),'credential','fill'],
                                input='protocol=https\nhost=github.com\n\n',
                                stdout=subprocess.PIPE,text=True,timeout=180,
                                env=dict(os.environ,GCM_TRACE='false',GCM_TRACE_SECRETS='false'))
    except subprocess.TimeoutExpired:
        raise RuntimeError('GitHub sign-in did not finish within three minutes. Retry and complete its sign-in prompt.') from None
    if result.returncode:
        raise RuntimeError('GitHub sign-in failed. Run this from your regular Windows terminal '
                           'so Git can use your credential manager, then retry.')
    values = dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    token = values.get('password')
    if not token:
        raise RuntimeError('Git did not supply a GitHub credential. Sign in through Git first.')
    return token


def request(token, path, data=None, method='GET', content_type='application/json', optional=False):
    url = path if path.startswith('https://') else 'https://api.github.com'+path
    body = json.dumps(data).encode() if data is not None and content_type=='application/json' else data
    req = Request(url,data=body,method=method,headers={
        'Authorization':'Bearer '+token, 'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28', 'Content-Type':content_type,
        'User-Agent':'seedsow-lua-editor-release'})
    try:
        with urlopen(req,timeout=60) as response:
            payload = response.read()
            return json.loads(payload) if payload else None
    except HTTPError as error:
        if optional and error.code==404:
            return None
        # Response headers and request credentials must never be included in errors.
        try:
            message = json.loads(error.read()).get('message','Request rejected.')
        except ValueError:
            message = 'Request rejected.'
        raise RuntimeError(f'GitHub HTTP {error.code}: {message}') from None


def uploaded_asset_matches(asset,path):
    return (asset.get('state')=='uploaded' and asset.get('size')==path.stat().st_size
            and asset.get('digest')=='sha256:'+hashlib.sha256(path.read_bytes()).hexdigest())


def publish(expected_head=None):
    if git('remote','get-url','origin') != REMOTE_URL:
        raise RuntimeError('origin is not the intended release repository.')
    if git('status','--porcelain'):
        raise RuntimeError('Commit or discard local source changes before publishing.')
    if git('branch','--show-current') != 'main':
        raise RuntimeError('Check out the prepared main branch first.')
    head = git('rev-parse','HEAD')
    remote = git('ls-remote','origin','refs/heads/main').split()
    remote_head = remote[0] if remote else None
    if remote_head != head:
        if expected_head:
            if remote_head != expected_head:
                raise RuntimeError('Remote main changed. Inspect it before publishing; no force update was attempted.')
            if int(git('rev-list','--count','HEAD')) != 1:
                raise RuntimeError('Replacing the first commit requires a prepared single-commit local history.')
            print('Replacing the known first commit with the prepared release commit.',flush=True)
            git('push','--force-with-lease=refs/heads/main:'+expected_head,'-u','origin','HEAD:main',capture=False)
        else:
            try:
                git('merge-base','--is-ancestor',remote_head or '',head)
            except RuntimeError:
                raise RuntimeError('Remote main is not an ancestor of the prepared commit. No history was replaced.') from None
            print('Pushing the new release commit normally.',flush=True)
            git('push','-u','origin','HEAD:main',capture=False)
    else:
        print('Remote main already matches the prepared commit.',flush=True)
    if git('ls-remote','origin','refs/heads/main').split()[0] != head:
        raise RuntimeError('Remote verification did not match the release commit.')
    print('Building the companion/source ZIP...',flush=True)
    info = package()
    version = (ROOT/'VERSION').read_text().strip()
    tag = 'v'+version
    token = credential()
    base = '/repos/'+REPOSITORY
    notes = (ROOT/'maintainer/RELEASE_NOTES.md').read_text(encoding='utf-8')
    existing = request(token,base+'/releases/tags/'+tag,optional=True)
    if existing is None:
        drafts = [r for r in request(token,base+'/releases?per_page=100') if r.get('tag_name')==tag]
        if len(drafts)>1:
            raise RuntimeError('Multiple draft releases use '+tag+'. Inspect them before publishing.')
        existing = drafts[0] if drafts else None
    if existing and not existing.get('draft'):
        raise RuntimeError('This version is already published. Choose a new version rather than replacing its assets.')
    print('Checking the ready-made save and download checksums...',flush=True)
    prepared_assets = release_assets(info)
    data = {'tag_name':tag,'target_commitish':head,'name':'Seedsow Lua Editor '+version,
            'body':notes,'draft':True,'prerelease':False}
    if existing:
        print('Resuming draft release '+tag+'...',flush=True)
        release = request(token,base+'/releases/'+str(existing['id']),data,'PATCH')
    else:
        print('Creating draft release '+tag+'...',flush=True)
        release = request(token,base+'/releases',data,'POST')
    if not release.get('draft'):
        raise RuntimeError('Only draft release assets can be uploaded or replaced.')
    assets = {a['name']:a for a in request(token,base+'/releases/'+str(release['id'])+'/assets?per_page=100')}
    if set(assets)-{p.name for p,_ in prepared_assets}:
        raise RuntimeError('The draft contains additional assets. Inspect them before making it public.')
    for path,kind in prepared_assets:
        if path.name in assets:
            if uploaded_asset_matches(assets[path.name],path):
                print('Already uploaded and verified '+path.name,flush=True)
                continue
            print('Replacing an incomplete or outdated draft asset: '+path.name,flush=True)
            request(token,base+'/releases/assets/'+str(assets[path.name]['id']),method='DELETE')
        print('Uploading '+path.name+' ('+str(path.stat().st_size)+' bytes)...',flush=True)
        url = 'https://uploads.github.com/repos/'+REPOSITORY+'/releases/'+str(release['id'])+'/assets?name='+quote(path.name)
        # Raw bytes, including JSON manifests, are sent unchanged.
        req = Request(url,data=path.read_bytes(),method='POST',headers={
            'Authorization':'Bearer '+token,'Content-Type':kind,
            'Accept':'application/vnd.github+json','User-Agent':'seedsow-lua-editor-release'})
        try:
            with urlopen(req,timeout=120) as response:
                asset = json.load(response)
        except HTTPError as error:
            raise RuntimeError(f'Asset upload failed (HTTP {error.code}); release remains a draft.') from None
        if asset.get('state')!='uploaded' or asset.get('size')!=path.stat().st_size:
            raise RuntimeError('Asset verification failed; release remains a draft.')
        print('Uploaded '+path.name,flush=True)
    release = request(token,base+'/releases/'+str(release['id']),{'draft':False,'make_latest':'true'},'PATCH')
    print('Published '+release['html_url'],flush=True)
    return release['html_url']


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-head',help='Exact known old main SHA, authorizing its replacement')
    args = parser.parse_args()
    if args.expected_head and not re.fullmatch('[0-9a-f]{40}',args.expected_head):
        parser.error('--expected-head must be a full commit SHA.')
    try:
        publish(args.expected_head)
    except KeyboardInterrupt:
        parser.exit(130,'Publishing stopped. Run the same command again to resume the draft.\n')
    except (RuntimeError,OSError) as error:
        parser.exit(1,'Release not completed: '+str(error)+'\n')
