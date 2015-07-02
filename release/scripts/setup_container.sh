#!/bin/bash

set -e
USER="python"

if [ `whoami` != "root" ];
then
  echo "Please run this as root"
  exit 1
fi

yum -y install gcc make vim git sudo wget tar zlib-devel bzip2 openssl-devel which nc
cd /root
[ ! -f Python-2.7.10.tgz ] && wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
tar -xvzf Python-2.7.10.tgz
cd Python-2.7.10
./configure --prefix=/usr --enable-shared --with-system-ffi
#--with-system-expat
make install
ln -s /usr/lib/libpython2.7.so.1.0 /lib64/libpython2.7.so.1.0
cd /root
wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-17.1.1.tar.gz#md5=7edec6cc30aca5518fa9bad42ff0179b
tar -xvzf setuptools-17.1.1.tar.gz
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
" > /usr/lib/python2.7/site-packages/PyInstaller/hooks/hook-boto.py
# Pyinstaller won't run as root
id ${USER} || useradd -m ${USER}
sudo -u ${USER} /vagrant/scripts/build_portable.sh
tarball="NuoDBAWSQuickstart_$(date +%s).tgz"
rm /repo/tmp/*.tgz
cp /tmp/installer.tgz /repo/tmp/${tarball}
[ -L /repo/tmp/latest.tgz ] && rm /repo/tmp/latest.tgz
ln -s /repo/tmp/${tarball} /repo/tmp/latest.tgz
echo "########################################"
echo " Created tarball /repo/tmp/${tarball}"
echo "########################################"

