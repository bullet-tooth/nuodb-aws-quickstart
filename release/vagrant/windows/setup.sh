#!/usr/bin/bash

set -e
USER="vagrant"

pip install pyinstaller
cd /cygdrive/c/repo
python setup.py install
echo "
import boto, inspect, os

datas = [
  (os.path.join(os.path.dirname(boto.__file__), 'endpoints.json'), 'boto'),
  (os.path.join(os.path.dirname(boto.__file__), 'cacerts', 'cacerts.txt'), os.path.join('boto', 'cacerts')),
]
" > /cygdrive/c/Python27/Lib/site-packages/PyInstaller/hooks/hook-boto.py
/cygdrive/c/vagrant/build.sh
