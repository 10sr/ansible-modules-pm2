#!/bin/sh
set -eux

base=$PWD

for dir in pm2tasks
do
    cd $base/$dir
    molecule test
done
