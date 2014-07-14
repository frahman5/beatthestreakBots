#!/bin/bash
## Script to semi-automate the process of creating VM instnaces, 
## and running player selectionss on them

# Used to wait for google cloud instances to finish up
function pause(){
   read -p "$*"
}
 
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
disk1=--disk="sn5vmn1,deviceName=sn1vmn1,mode=READ_WRITE,boot"
disk2=--disk="sn5vmn2,deviceName=sn1vmn1,mode=READ_WRITE,boot"
autodelete=--auto_delete_boot_disk="true"
   # instance names
sN5vMN1=sn5vmn1
sN5vMN2=sn5vmn2

## Home Computer parameters
minionFiles=/users/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles/
sN5vMN1Excel="sN=5,vMN=1.xlsx"
sN5vMN2Excel="sN=5,vMN=2.xlsx"
## Spin up instances in series
    # Instance 1
gcutil $sv $p adddisk $sN5vMN1 $zone $snapshot $disktype
gcutil $sv $p addinstance $sN5vMN1 $zone $machinetype $network $ip $service $disk1 $autodelete
    # Instance 2
gcutil $sv $p adddisk $sN5vMN2 $zone $snapshot $disktype
gcutil $sv $p addinstance $sN5vMN2 $zone $machinetype $network $ip $service $disk2 $autodelete

## SSH into them and then run launch scripts inside of them
pause 'Press [Enter] after 15-20 seconds to continue before ssh-ing into new instance  '
   ## First instance
gcutil push $p $sN5vMN1 go.sh /home/faiyamrahman/
gcutil push $p $sN5vMN1 $minionFiles$sN5vMN1Excel $googleMinionDir
gcutil $sv $p ssh $zone $sN5vMN1
   ## Second instance
gcutil push $p $sN5vMN2 go.sh /home/faiyamrahman/
gcutil push $p $sN5vMN2 $minionFiles$sN5vMN2Excel $googleMinionDir
gcutil $sv $p ssh $zone $sN5vMN2
