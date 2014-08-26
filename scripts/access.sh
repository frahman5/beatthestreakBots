#!/bin/bash
## A script to ssh into an instance 

gcutil --service_version="v1" --project="coherent-code-678" ssh --zone="us-central1-a" "sn"$1
