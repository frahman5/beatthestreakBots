#!/bin/bash
## A script to update the snapshot 

## Google Compute Engine Paraaters
googleMinionDir=/home/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles
sv=--service_version="v1"
p=--project="faiyam-bts-1"
zone=--zone="us-central1-a"
snapshot=--source_snapshot="sims-chromedriver-clientalive-strats-5-17"
disktype=--disk_type="pd-ssd"
machinetype=--machine_type="n1-standard-1"
network=--network="default"
ip=--external_ip_address="ephemeral"
service=--service_account_scopes="https://www.googleapis.com/auth/devstorage.read_only"
tags=--tags="http-server,https-server"
autodelete=--auto_delete_boot_disk="true"

## Home Computer parameters
finalMinionDir=/users/faiyamrahman/Desktop/final/minions/

function makeDisk {
    # strategyNumber -> None
    # Given e.g input 5, makes disk sn5 from snapshot
    gcutil $sv $p adddisk 'sn'$1 $zone $snapshot $disktype
}

function makeInstance {
    # strategyNumber -> None
    # Given e.g input 5, makes instance sn5. Assumes disk sn5 has already been
    # created
    disk='--disk=sn'$1',deviceName=sn'$1',mode=READ_WRITE,boot'
    gcutil $sv $p addinstance 'sn'$1 $zone $machinetype $network $ip $service $disk $autodelete
}

# make sn5 and ssh into it so we can pull the git repo
makeDisk 5
makeInstance 5
gcutil $sv $p ssh $zone sn5

# update the snapshot
gcutil --project='faiyam-bts-1' deletesnapshot "sims-chromedriver-clientalive-strats-5-17"
gcutil --project='faiyam-bts-1' addsnapshot --zone='us-central1-a' "sims-chromedriver-clientalive-strats-5-17"

# delete the instance
gcutil --project='faiyam-bts-1' deleteinstance sn5

# list the snapshots
gcutil --project='faiyam-bts-1' listsnapshots