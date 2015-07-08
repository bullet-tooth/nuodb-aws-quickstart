#!/bin/bash

TARBALL=$1
COMMAND=$2
# This command is run by the test.py script inside the container to actually execute the script in question. 

# Make sure tar command is installed
yum -y install tar &> /dev/null
apt-get -y install tar &> /dev/null
cd /tmp
tar -xzf ${TARBALL}
cd NuoDBAWSQuickstart
$COMMAND