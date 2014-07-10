#!/bin/bash
### A script to automate the process of SSHing into various google cloud VMs 
### and telling them to choose my players for the day

## SSH into a google cloud VM and run the chooseplayer script
gcutil --service_version="v1" --project="faiyam-bts-1" ssh --zone="us-central1-a" "production-instance-c"  screen
