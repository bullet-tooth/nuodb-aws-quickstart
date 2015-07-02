#!/bin/bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
#vagrant destroy -f
vagrant up
vagrant ssh tarballBuild0 -c "docker run -it -v /vagrant:/vagrant -v /repo:/repo centos:5 /vagrant/scripts/setup_container.sh"
$DIR/test.py
vagrant destroy -f