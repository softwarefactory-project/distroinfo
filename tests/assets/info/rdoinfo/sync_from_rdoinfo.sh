#!/bin/bash

RDOINFO_RAW=https://raw.githubusercontent.com/redhat-openstack/rdoinfo/master

SYNCFILES="rdo.yml deps.yml rdo-full.yml"
rm -f $SYNCFILES
for f in $SYNCFILES; do
    wget "$RDOINFO_RAW/$f"
done
