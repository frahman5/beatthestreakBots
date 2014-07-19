#!/bin/bash
## Test script to see if we can go our google virtual machine creation
## in parallel instead of in series

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


## For each strategy, create commands
dPrefix="gcutil $sv $p adddisk sn"
dSuffix=" $zone $snapshot $disktype"

iPrefix="gcutil $sv $p addinstance sn"
iMidfix=" $zone $machinetype $network $ip $service "
iSuffix=" $autodelete"

   # Create disk creation commands
       # the sed part removes all the backslashes
cmd5D=$(printf "%q%q%q" "$dPrefix" "5" "$dSuffix" | sed "s/\\\\//g")
cmd6D=$(printf "%q%q%q" "$dPrefix" "6" "$dSuffix" | sed "s/\\\\//g")
cmd7D=$(printf "%q%q%q" "$dPrefix" "7" "$dSuffix" | sed "s/\\\\//g")
cmd8D=$(printf "%q%q%q" "$dPrefix" "8" "$dSuffix" | sed "s/\\\\//g")
cmd9D=$(printf "%q%q%q" "$dPrefix" "9" "$dSuffix" | sed "s/\\\\//g")
cmd10D=$(printf "%q%q%q" "$dPrefix" "10" "$dSuffix" | sed "s/\\\\//g")
cmd11D=$(printf "%q%q%q" "$dPrefix" "11" "$dSuffix" | sed "s/\\\\//g")
cmd12D=$(printf "%q%q%q" "$dPrefix" "12" "$dSuffix" | sed "s/\\\\//g")
cmd13D=$(printf "%q%q%q" "$dPrefix" "13" "$dSuffix" | sed "s/\\\\//g")
cmd14D=$(printf "%q%q%q" "$dPrefix" "14" "$dSuffix" | sed "s/\\\\//g")
cmd15D=$(printf "%q%q%q" "$dPrefix" "15" "$dSuffix" | sed "s/\\\\//g")
cmd16D=$(printf "%q%q%q" "$dPrefix" "16" "$dSuffix" | sed "s/\\\\//g")
cmd17D=$(printf "%q%q%q" "$dPrefix" "17" "$dSuffix" | sed "s/\\\\//g")

    # Create instance creation commands
cmd5I=$(printf "%q%q%q%q%q" "$iPrefix" "5" "$iMidfix" "$disk5" "$iSuffix" | sed "s/\\\\//g")
cmd6I=$(printf "%q%q%q%q%q" "$iPrefix" "6" "$iMidfix" "$disk6" "$iSuffix" | sed "s/\\\\//g")


# echo $cmd5I
# echo $cmd6I

# cmd5I=$iPrefix'5'$iMidfix$disk5$iSuffix
# cmd6I=$iPrefix'6'$iMidfix$disk6$iSuffix

echo $cmd5I
echo $cmd6I
# # cmd5I=
# # cmd5D="gcutil $sv $p adddisk sn5 $zone $snapshot $disktype"
# # cmd5I="gcutil $sv $p addinstance sn5 $zone $machinetype $network $ip $service $disk5 $autodelete"

# # cmd6D="gcutil $sv $p adddisk sn6 $zone $snapshot $disktype"
# # cmd6I="gcutil $sv $p addinstance sn6 $zone $machinetype $network $ip $service $disk6 $autodelete"

# Create all the disks in parallel
$cmd5D & $cmd6D & wait # wait makes shell wait for all jobs runnign background to finish
echo "**************** DISKS CREATED! ****************"

## Create all the instances in parallel
$cmd5I & $cmd6I & wait
echo "**************** INSTANCES CREATED! ****************"
