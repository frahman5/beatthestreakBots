#!/bin/bash

## A script to run on the virtual machines to choose players

## Get strategy and virtual machine numbers
sN=$1
d=$2

## Run them both
bash go.sh $sN 1 $d & bash go.sh $sN 2 $d &
exit
