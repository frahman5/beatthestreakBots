#!/bin/bash
## A script to ssh into an instance 

gcutil --service_version="v1" --project="dmitry-bts-1" ssh --zone="us-central1-a" "sn"$1
