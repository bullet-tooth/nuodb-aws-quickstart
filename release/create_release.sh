#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPODIR="$DIR/.."
TMPDIR="$REPODIR/tmp"
ARTIFACTDIR="$TMPDIR/NuoDBAWSQuickstart"
echo $ARTIFACTDIR
[ -d $ARTIFACTDIR ] && rm -rf $ARTIFACTDIR
mkdir $ARTIFACTDIR
exit
for vagrantfile in `find $DIR/vagrant -name Vagrantfile`;
do
  osdir=`basename $vagrantfile`
  os=`basename $osdir`
  echo "Creating artifact for ${os^^}"
  cd $osdir
  vagrant up
  [ -f post.sh ] && post.sh
  vagrant destroy
done