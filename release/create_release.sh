#!/bin/bash
set -e
# set -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/env.sh
ARTIFACTDIR="$DIR/artifacts"
PROJECTDIR="$ARTIFACTDIR/${PROJECT}"
LOGFILE="$DIR/${0}.log"

function period() {
  echo -n "."
}

function pre() {
  # Pre-checks 
  which vagrant &> /dev/null 
  if [ $? -ne 0 ];
  then
    echo "This script requires that Vagrant and VirtualBox be installed on this host."
    echo "Please install Vagrant: http://www.vagrantup.com"
    echo "and VirtualBox: https://www.virtualbox.org/wiki/Downloads"
    exit 2
  fi
  fail=0
  for command in "rsync tar ";
  do
	  which $command &> /dev/null
	  if [ $? -ne 0 ];
	  then
	    echo "This script requires that $command be installed on this host."
	    fail=1
	  fi
  done
  [ $fail -eq 1 ] && exit 2
  
  # Start work
  echo "Script started $(date)"
  [ -d $PROJECTDIR ] && rm -rf $PROJECTDIR
  mkdir -p $PROJECTDIR
  echo "Logging to $LOGFILE"
  echo "Artifact output to $ARTIFACTDIR"
}

function post() {
  id=$(date -u +%s)
  cd $PROJECTDIR
  for os in `find * -maxdepth 0 -type d`;
  do
    cd $PROJECTDIR/${os}
    name="${PROJECT}_${id}_${os}"
    
    echo "Compressing artifact for ${os}"
	  if [ "${os}" == "Windows" ];
	  then
	    filename="${name}.zip"
	    zip -r $filename ${PROJECT}
    else
      filename="${name}.tgz"
	    tar -czf $filename ${PROJECT}
	  fi
	  mv $filename ${ARTIFACTDIR}/
    echo "Created artifact $ARTIFACTDIR/$filename"
  done
  cd $ARTIFACTDIR
  rm -rf $PROJECTDIR
  echo "Script complete $(date)"
}

function build() 
{
  osdir=`dirname $vagrantfile`
  os=`basename $osdir | tr '[:lower:]' '[:upper:]'`
  echo -n "Creating artifact for ${os}"
  cd $osdir
  period
  echo "# Cleaning up old ${os} vagrant boxes" >> $LOGFILE
  vagrant destroy -f &> $LOGFILE
  [ -f pre.sh ] && ./pre.sh &> $LOGFILE
  echo "# Starting up ${os} vagrant machine" >> $LOGFILE
  vagrant up &> $LOGFILE
  period
  [ -f test.sh ] && ./test.sh &> $LOGFILE
  period
  [ -f post.sh ] && ./post.sh &> $LOGFILE
  period
  vagrant destroy -f &> $LOGFILE
  period
  echo "################" >> $LOGFILE
  echo "# COMPLETED BUILD FOR ${os}" >> $LOGFILE
  echo "################" >> $LOGFILE
  echo
}

function buildlinux() 
{
  vagrantfile="$DIR/vagrant/linux/Vagrantfile"
  build
}

function buildosx() {
  vagrantfile="$DIR/vagrant/osx/Vagrantfile"
  build
}

function buildwindows() {
  vagrantfile="$DIR/vagrant/windows/Vagrantfile"
  build
}

function buildall() {
  pre
  buildlinux
  buildosx
  buildwindows
  post
}

function help() {
  echo "This script will build a portable artifact from this repository for each of the following platforms: Linux, OSX, Windows"
  echo "It does so by creating vagrant machines for each type and building the artifacts individually, then tar them together."
  echo "Usage: $0 [all|windows|linux|osx]"
}

case "$1" in
  "all")  buildall;;
  "windows") pre; buildwindows; post;;
  "linux") pre; buildlinux; post;;
  "osx") pre; buildosx; post;;
  *) help;
esac
