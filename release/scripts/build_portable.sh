#!/bin/bash
set -e

HOME=/home/python

cd ${HOME}
[ -d NuoDBAWSQuickstart ] && rm -rf NuoDBAWSQuickstart
mkdir NuoDBAWSQuickstart
for file in `find /repo/bin -type f`;
do
  echo "##### INSTALLING ${file}"
  pyinstaller --distpath=${HOME}/NuoDBAWSQuickstart --hidden-import=pkg_resources -F ${file}
done
tar -C ${HOME} -cvzf /tmp/installer.tgz NuoDBAWSQuickstart