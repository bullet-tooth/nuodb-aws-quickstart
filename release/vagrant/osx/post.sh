#!/bin/bash
set -e


DEBUG=0
source "$(pwd)/../../env.sh"

targetDir="$(pwd)/../../artifacts/${PROJECT}/"

echo "##### Copying OSX artifacts into $targetDir"

# vagrant ssh-config spits out a long string of words. parse this into variables
item_is_key=1
for word in `vagrant ssh-config`;
do
  if [ $item_is_key -eq 1 ];
  then
    key=$word
    item_is_key=0
  else
    [ $DEBUG -eq 1 ] && echo "$key=$word"
    declare "$key=$word"
    item_is_key=1
  fi
done
rsync -av -e "ssh -p ${Port} -i ${IdentityFile} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" ${User}@${HostName}:/tmp/${PROJECT}/* $targetDir