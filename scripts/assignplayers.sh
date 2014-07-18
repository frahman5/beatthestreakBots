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
autodelete=--auto_delete_boot_disk="true"

## Home Computer parameters
minionFiles=/users/faiyamrahman/programming/Python/beatthestreakBots/accountFiles/minionAccountFiles/
sN5vMN1Excel="sN=5,vMN=1.xlsx"
sN5vMN2Excel="sN=5,vMN=2.xlsx"

## Disk names
disk5_1=--disk="sn5vmn1,deviceName=sn5vmn1,mode=READ_WRITE,boot"
disk5_2=--disk="sn5vmn2,deviceName=sn5vmn2,mode=READ_WRITE,boot"

disk6_1=--disk="sn6vmn1,deviceName=sn6vmn1,mode=READ_WRITE,boot"
disk6_2=--disk="sn6vmn2,deviceName=sn6vmn2,mode=READ_WRITE,boot"

disk7_1=--disk="sn7vmn1,deviceName=sn7vmn1,mode=READ_WRITE,boot"
disk7_2=--disk="sn7vmn2,deviceName=sn7vmn2,mode=READ_WRITE,boot"

disk8_1=--disk="sn8vmn1,deviceName=sn8vmn1,mode=READ_WRITE,boot"
disk8_2=--disk="sn8vmn2,deviceName=sn8vmn2,mode=READ_WRITE,boot"

disk9_1=--disk="sn9vmn1,deviceName=sn9vmn1,mode=READ_WRITE,boot"
disk9_2=--disk="sn9vmn2,deviceName=sn9vmn2,mode=READ_WRITE,boot"

disk10_1=--disk="sn10vmn1,deviceName=sn10vmn1,mode=READ_WRITE,boot"
disk10_2=--disk="sn10vmn2,deviceName=sn10vmn2,mode=READ_WRITE,boot"

disk11_1=--disk="sn11vmn1,deviceName=sn11vmn1,mode=READ_WRITE,boot"
disk11_2=--disk="sn11vmn2,deviceName=sn11vmn2,mode=READ_WRITE,boot"

disk12_1=--disk="sn12vmn1,deviceName=sn12vmn1,mode=READ_WRITE,boot"
disk12_2=--disk="sn12vmn2,deviceName=sn12vmn2,mode=READ_WRITE,boot"

disk13_1=--disk="sn13vmn1,deviceName=sn13vmn1,mode=READ_WRITE,boot"
disk13_2=--disk="sn13vmn2,deviceName=sn13vmn2,mode=READ_WRITE,boot"

disk14_1=--disk="sn14vmn1,deviceName=sn14vmn1,mode=READ_WRITE,boot"
disk14_2=--disk="sn14vmn2,deviceName=sn14vmn2,mode=READ_WRITE,boot"

disk15_1=--disk="sn15vmn1,deviceName=sn15vmn1,mode=READ_WRITE,boot"
disk15_2=--disk="sn15vmn2,deviceName=sn15vmn2,mode=READ_WRITE,boot"

disk16_1=--disk="sn16vmn1,deviceName=sn16vmn1,mode=READ_WRITE,boot"
disk16_2=--disk="sn16vmn2,deviceName=sn16vmn2,mode=READ_WRITE,boot"

disk17_1=--disk="sn17vmn1,deviceName=sn17vmn1,mode=READ_WRITE,boot"
disk17_2=--disk="sn17vmn2,deviceName=sn17vmn2,mode=READ_WRITE,boot"

## Spin up instances in series
    # First the disks
for disk in sn5vmn1 sn5vmn2 sn6vmn1 sn6vmn2 sn7vmn1 sn7vmn2 sn8vmn1 sn8vmn2 \
            sn9vmn1 sn9vmn2 sn10vmn1 sn10vmn2 sn11vmn1 sn11vmn2 sn12vmn1 sn12vmn2 \
            sn13vmn1 sn13vmn2 sn14vmn1 sn14vmn2 sn15vmn1 sn15vmn2 sn16vmn1 sn16vmn2 \
            sn17vmn1 sn17vmn2 
do
    gcutil $sv $p adddisk $disk $zone $snapshot $disktype
done

    ## Then the instances
for pair in "sn5vmn1 $disk5_1" "sn5vmn2 $disk5_2" "sn6vmn1 $disk6_1" \
            "sn6vmn2 $disk6_2" "sn7vmn1 $disk7_1" "sn7vmn2 $disk7_2" \
            "sn8vmn1 $disk8_1" "sn8vmn2 $disk8_2" "sn9vmn1 $disk9_1" \
            "sn9vmn2 $disk9_2" "sn10vmn1 $disk10_1" "sn10vmn2 $disk10_2" \
            "sn11vmn1 $disk11_1" "sn11vmn2 $disk11_2" "sn12vmn1 $disk12_1" \
            "sn12vmn2 $disk12_2" "sn13vmn1 $disk13_1" "sn13vmn2 $disk13_2" \
            "sn14vmn1 $disk14_1" "sn14vmn2 $disk14_2" "sn15vmn1 $disk15_1" \
            "sn15vmn2 $disk15_2" "sn16vmn1 $disk16_1" "sn16vmn2 $disk16_2" \
            "sn17vmn1 $disk17_1" "sn17vmn2 $disk17_2"
do
    set -- $pair
    gcutil $sv $p addinstance $1 $zone $machinetype $network $ip $service $2 $autodelete
done

    ## Then give them the necessary files, SSH in, and launch scripts
pause 'Press [Enter] after 15-20 seconds to continue before ssh-ing into new instance  '

for instance in sn5vmn1 sn5vmn2 sn6vmn1 sn6vmn2 sn7vmn1 sn7vmn2 sn8vmn1 sn8vmn2 \
                sn9vmn1 sn9vmn2 sn10vmn1 sn10vmn2 sn11vmn1 sn11vmn2 sn12vmn1 sn12vmn2 \
                sn13vmn1 sn13vmn2 sn14vmn1 sn14vmn2 sn15vmn1 sn15vmn2 sn16vmn1 sn16vmn2 \
                sn17vmn1 sn17vmn2 
do
    gcutil push $p $instance go.sh /home/faiyamrahman
    # add in the minion push after the first day
    gcutil $sv $p ssh $zone $instance
done

#    ## First instance
# gcutil push $p $sN5vMN1 go.sh /home/faiyamrahman/
# gcutil push $p $sN5vMN1 $minionFiles$sN5vMN1Excel $googleMinionDir
# gcutil $sv $p ssh $zone $sN5vMN1
#    ## Second instance
# gcutil push $p $sN5vMN2 go.sh /home/faiyamrahman/
# gcutil push $p $sN5vMN2 $minionFiles$sN5vMN2Excel $googleMinionDir
# gcutil $sv $p ssh $zone $sN5vMN2
