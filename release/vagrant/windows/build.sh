#!/usr/bin/bash
set -e

source /cygdrive/c/repo/release/env.sh

echo "BUILDING ARTIFACT"
DISTDIR='C:\\repo\\release\\artifacts\\'${PROJECT}'\\Windows\\'${PROJECT}
mkdir -p $DISTDIR

cd ${HOME}
for file in `find /cygdrive/c/repo/bin -type f`;
do
  filename=`basename $file`
  echo "##### INSTALLING ${file}"
  pyinstaller --distpath=$DISTDIR --paths=C:\\Python27\\Lib --hidden-import=pkg_resources -F C:\\repo\\bin\\$filename
  echo "##### CREATED ${DISTDIR}/${filename}"
done
