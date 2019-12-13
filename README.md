# CloudFlare Dynamic IP Script

This script will take the settings in the .env file you provide (copy env.sample to .env to get started) and update Cloudflare with your public IP address so that traffic can be routed in a fairly stable manner back to your server/services behind your dynamic IP address.

## Getting started

1. Copy env.sample to '.env'
2. Edit the settings in the .env file as instructed by .env file
3. Install poetry
4. Run 'poetry install' (mine installs the virtual env in the ./.venv - yours may be different)
5. activate the virtual env (e.g. poetry shell)
6. Add A records in Cloudflare for the domains you want to point to your public IP (recommend using obviously bad IP addresses so you can check that they are updated correctly with your public IP address)
7. Run the script `dyndns.py` (make sure it's executable)
8. Make sure it updated your IP addresses for your domains in Cloudflare
9. It should have also created a CACHE.json file with identifiers it found for your zone and domains from Cloudflare
10. Setup your cronjob to run every X minutes so that when your public IP address is updated, your servers will be updated within X minutes

Crontab command

    */5 * * * * /usr/bin/env bash -c 'cd /home/user/cf_dyndns && source .venv/bin/activate && ./dyndns.py'

NOTE: Update /home/user/cf_dyndns with the actual location of this script folder

## Background Notes

[Current public IP address endpoint](http://ipinfo.io/ip) - using this to find my public IP - more options are listed in StackOverflow question below

[Cloudflare API v4 Documentation](https://api.cloudflare.com/#dns-records-for-a-zone-update-dns-record)

[c# - Get public/external IP address? - Stack Overflow](https://stackoverflow.com/questions/3253701/get-public-external-ip-address/45242105)
