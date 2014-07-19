#!/bin/bash
## Script to semi-automate the process of creating VM instnaces, 
## and running player selectionss on them

## Google Compute Engine Paraaters
googleMinionDir=/home/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles
sv=--service_version="v1"
p=--project="faiyam-bts-1"
zone=--zone="us-central1-a"
snapshot=--source_snapshot="sims-chromedriver-clientalive-strats-5-6-7"
disktype=--disk_type="pd-ssd"
machinetype=--machine_type="n1-standard-1"
network=--network="default"
ip=--external_ip_address="ephemeral"
service=--service_account_scopes="https://www.googleapis.com/auth/devstorage.read_only"
tags=--tags="http-server,https-server"
autodelete=--auto_delete_boot_disk="true"

## Home Computer parameters
minionFiles=/users/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles/
finalMinionDir=/users/faiyamrahman/Desktop/final/minions/
sN5vMN1Excel="sN=5,vMN=1.xlsx"
sN5vMN2Excel="sN=5,vMN=2.xlsx"

## Disk names
disk5=--disk="sn5,deviceName=sn5,mode=READ_WRITE,boot"
disk6=--disk="sn6,deviceName=sn6,mode=READ_WRITE,boot"
disk7=--disk="sn7,deviceName=sn7,mode=READ_WRITE,boot"
disk8=--disk="sn8,deviceName=sn8,mode=READ_WRITE,boot"
disk9=--disk="sn9,deviceName=sn9,mode=READ_WRITE,boot"
disk10=--disk="sn10,deviceName=sn10,mode=READ_WRITE,boot"
disk11=--disk="sn11,deviceName=sn11,mode=READ_WRITE,boot"
disk12=--disk="sn12,deviceName=sn12,mode=READ_WRITE,boot"
disk13=--disk="sn13,deviceName=sn13,mode=READ_WRITE,boot"
disk14=--disk="sn14,deviceName=sn14,mode=READ_WRITE,boot"
disk15=--disk="sn15,deviceName=sn15,mode=READ_WRITE,boot"
disk16=--disk="sn16,deviceName=sn16,mode=READ_WRITE,boot"
disk17=--disk="sn17,deviceName=sn17,mode=READ_WRITE,boot"

# ## Spin up instances in series
#     # First the disks
# for disk in sn5, sn6, sn7, sn8, sn9, sn10, sn11, sn12, sn13, sn14, sn15, sn16, sn17
# do
#     gcutil $sv $p adddisk $disk $zone $snapshot $disktype
# done

## For each strategy, make the disk, then make the instance
for pair in "sn5 $disk5" "sn6 $disk6" "sn7 $disk7" "sn8 $disk8" "sn9 $disk9" \
            "sn10 $disk10" "sn11 $disk11" "sn12 $disk12" "sn13 $disk13" \
            "sn14 $disk14"  "sn15 $disk15" "sn16 $disk16" "sn17 $disk17"
do
    set -- $pair
       # make the disk
    gcutil $sv $p adddisk $1 $zone $snapshot $disktype
       # make the instance
    gcutil $sv $p addinstance $1 $zone $machinetype $network $ip $service $2 $autodelete
done

## Then give them the necessary files, SSH in, and launch scripts
for strategy in 5 6 7 8 9 10 11 12 13 14 15 16 17
do
    minion1='sN='$strategy',vMN=1.xlsx'
    minion2='sN='$strategy',vMN=2.xlsx'
    instance='sn'$strategy
        # push the launch script
    gcutil push $p $instance go.sh /home/faiyamrahman 
        # push the minion account files
    gcutil push $p $instance $finalMinionDir$minion1 $googleMinionDir 
    gcutil push $p $instance $finalMinionDir$minion2 $googleMinionDir 
        # ssh in and launch both strategies. REMEMBER:
            # Launch a screen, run go.sh for vmn 1, then another screen
            # then go.sh for vmn2, then ctrl+a, d to detach from the screen,
            # then exit the instance
    gcutil $sv $p ssh $zone $instance
done
