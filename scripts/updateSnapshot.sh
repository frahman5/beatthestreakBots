#!/bin/bash
## A script to update the snapshot 

gcutil --project='faiyam-bts-1' removesnapshot "sims-chromedriver-clientalive-strats-5-17"
gcutil --project='faiyam-bts-1' addsnapshot --zone='us-central1-a'