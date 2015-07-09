#!/bin/bash

set -e
USER="vagrant"

if [ `whoami` != "root" ];
then
  echo "Please run this as root"
  exit 1
fi

cd /tmp
curl -o /tmp/setuptools.tar.gz https://pypi.python.org/packages/source/s/setuptools/setuptools-17.1.1.tar.gz
tar -xvzf setuptools.tar.gz
cd setuptools-17.1.1
python setup.py install
easy_install pip
pip install pyinstaller
cd /repo
python setup.py install
echo "
import boto, inspect, os

datas = [
  (os.path.join(os.path.dirname(boto.__file__), 'endpoints.json'), 'boto'),
  (os.path.join(os.path.dirname(boto.__file__), 'cacerts', 'cacerts.txt'), os.path.join('boto', 'cacerts')),
]
" > /Library/Python/2.7/site-packages/PyInstaller/hooks/hook-boto.py
# Pyinstaller won't run as root
sudo -u ${USER} /vagrant/build.sh
