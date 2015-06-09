#!/usr/bin/env python3

import codecs
import functools
import json
import os
import requests
import subprocess
import tempfile

@functools.lru_cache()
def get_npm_version(package):
    r = requests.get('https://registry.npmjs.org/%s' % package)
    version = r.json()['dist-tags']['latest']
    print('Latest %s: %s' % (package, version))
    return version

@functools.lru_cache()
def get_packagist_version(package):
    r = requests.get('https://packagist.org/packages/%s.json' % package)
    resp = r.json()['package']['versions']
    normalized = set()
    for ver in resp:
        if not ver.startswith('dev-'):
            if ver.startswith('v'):
                normalized.add(ver[1:])
            else:
                normalized.add(ver)
    version = max(normalized)
    print('Latest %s: %s' % (package, version))
    return version

def commit_and_push(files, msg, branch, topic):
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(bytes(msg, 'utf-8'))
    f.close()
    subprocess.check_call(['git', 'add'] + files)
    subprocess.check_call(['git', 'commit', '-F', f.name])
    subprocess.check_call(['git', 'push', 'gerrit', 'HEAD:refs/for/{0}%topic={1}'.format(branch, topic)])
    os.unlink(f.name)

if os.path.isdir('/data/project/ci'):
    # Running on Tool labs
    EXTENSIONS_DIR = '/data/project/ci/src/extensions'
else:
    # Legoktm's laptop
    EXTENSIONS_DIR = '/home/km/projects/vagrant/mediawiki/extensions'


def update_submodules_and_stuff(path):
    cwd = os.getcwd()
    os.chdir(path)
    subprocess.check_call(['git', 'pull'])
    subprocess.check_call(['git', 'submodule', 'update', '--init'])
    os.chdir(cwd)

def json_load(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        info = json.loads(f.read())
    return info
