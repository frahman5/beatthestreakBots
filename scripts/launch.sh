#!/bin/bash
## Script to semi-automate the process of creating VM instnaces, 
## and running player selectionss on them

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

function pushFiles {
    # strategyNumber -> None
    # Pushes a launch script and minion account files to the instance
    # for the given strategy

    # Create the necessary variables
    minion1='sN='$1',vMN=1.xlsx'
    minion2='sN='$1',vMN=2.xlsx'
    instance='sn'$1

    # push the launch script
    gcutil push $p $instance go.sh /home/faiyamrahman 

    # push the minion account files
    gcutil push $p $instance $finalMinionDir$minion1 $googleMinionDir 
    gcutil push $p $instance $finalMinionDir$minion2 $googleMinionDir 
}

## Create all the disks in parallel
    # wait makes shell wait for all jobs running background to finish
# makeDisk 5 & makeDisk 6 & makeDisk 7 & makeDisk 8 & makeDisk 9 & makeDisk 10 & \
# makeDisk 11 & makeDisk 12 & makeDisk 13 & makeDisk 14 & makeDisk 15 & makeDisk 16 & \
# makeDisk 17 & wait 
# echo "**************** DISKS CREATED! ****************"

# ## Create all the instances in parallel
# makeInstance 5 & makeInstance 6 & makeInstance 7 & makeInstance 8 & \
# makeInstance 9 & makeInstance 10 & makeInstance 11 & makeInstance 12 & \
# makeInstance 13 & makeInstance 14 & makeInstance 15 & makeInstance 16 & \
# makeInstance 17 & wait 
# echo "**************** INSTANCES CREATED! ****************"

# # Sleep for a bit to make sure instances are ready to receive files
# sleepTime=15
# echo "\n-->Sleeping for $sleepTime seconds to allow instances to be ready to receive files"
# sleep $sleepTime

# ## Push all the files in parallel
# pushFiles 5 & pushFiles 6 & pushFiles 7 & pushFiles 8 & pushFiles 9 & pushFiles 10 & \
# pushFiles 11 & pushFiles 12 & pushFiles 13 & pushFiles 14 & pushFiles 15 & pushFiles 16 & \
# pushFiles 17 & wait 
# echo "**************** FILES PUSHED! ****************"

## SSH into each one and launch your bots!
for strategy in 5 6 7 8 9 10 11 12 13 14 15 16 17
do
    gcutil $sv $p ssh $zone 'sn'$strategy
done
