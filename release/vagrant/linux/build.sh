#!/bin/bash
set -e

source /repo/release/env.sh

HOME=/home/vagrant
DISTDIR=/repo/release/artifacts/$PROJECT/Linux/$PROJECT
mkdir -p $DISTDIR

cd ${HOME}
for file in `find /repo/bin -type f`;
do
  echo "##### INSTALLING ${file}"
  pyinstaller --distpath=$DISTDIR --hidden-import=pkg_resources -F ${file}
  echo "##### CREATED ${DISTDIR}/$(basename $file)"
done
