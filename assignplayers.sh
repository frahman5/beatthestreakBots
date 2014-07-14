

gcutil --service_version="v1" --project="faiyam-bts-1" adddisk "production-instance-a" --zone="us-central1-a" --source_snapshot="sims-chromedriver-clientalive-strats-5-6-7" --disk_type="pd-ssd"

gcutil --service_version="v1" --project="faiyam-bts-1" addinstance "production-instance-a" --zone="us-central1-a" --machine_type="n1-standard-1" --network="default" --external_ip_address="ephemeral" --service_account_scopes="https://www.googleapis.com/auth/devstorage.read_only" --tags="http-server,https-server" --disk="production-instance-a,deviceName=production-instance-a,mode=READ_WRITE,boot" --auto_delete_boot_disk="true"