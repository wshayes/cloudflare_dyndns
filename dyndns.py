#!/usr/bin/env python
# -*-coding: utf-8 -*-

"""
Usage: $ {1: program}.py


"""

import copy
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

CF_EMAIL = os.getenv("CF_EMAIL")
CF_API_KEY = os.getenv("CF_API_KEY")
CF_API = os.getenv("CF_API", default="https://api.cloudflare.com/client/v4")
CF_ZONE_ID = os.getenv("CF_ZONE_ID")
ZONE = os.getenv("ZONE")

DOMAINS = [domain.strip() for domain in os.getenv("DOMAINS").split(",")]

# IP Address service url
IP_API = "http://ipinfo.io/ip"

# Cache values like zone_id that had to be collected first time this ran
try:
    with open("CACHE.json", "r") as f:
        CACHE = json.load(f)
except Exception:
    CACHE = {}

# curl -X PUT "https://api.cloudflare.com/client/v4/zones/023e105f4ecef8ad9ca31a8372d0c353/dns_records/372e67954025e0ba6aaa6d586b9e0b59" \
#      -H "X-Auth-Email: user@example.com" \
#      -H "X-Auth-Key: c2547eb745079dac9320b638f5e225cf483cc5cfdda41" \
#      -H "Content-Type: application/json" \
#      --data '{"type":"A","name":"example.com","content":"127.0.0.1","ttl":{},"proxied":false}'


def get_zone_id():

    headers = {
        "X-AUTH-KEY": CF_API_KEY,
        "X-AUTH-EMAIL": CF_EMAIL,
        "CONTENT-TYPE": "application/json",
    }
    r = requests.get(f"{CF_API}/zones", headers=headers)
    results = r.json()

    zone_id = [zone["id"] for zone in results["result"] if zone["name"] == ZONE][0]
    CACHE["zone_id"] = zone_id


def get_domain_ids():

    headers = {
        "X-AUTH-KEY": CF_API_KEY,
        "X-AUTH-EMAIL": CF_EMAIL,
        "CONTENT-TYPE": "application/json",
    }
    r = requests.get(f"{CF_API}/zones/{CACHE['zone_id']}/dns_records", headers=headers)
    results = r.json()

    # print("DumpVar:\n", json.dumps(results, indent=4))

    identifiers = {
        domain["name"]: domain["id"] for domain in results["result"] if domain["name"] in DOMAINS
    }
    CACHE["domain_ids"] = copy.copy(identifiers)


def get_public_ip():
    """Get public ip address for dynamic ip hosted service"""

    r = requests.get(IP_API)
    ip = r.text.strip()

    return ip


def save_cache():
    with open("CACHE.json", "w") as f:
        json.dump(CACHE, f, indent=4)


def update_cloudflare(ip):
    """Update Cloudflare"""

    for domain in DOMAINS:
        zone_id = CACHE["zone_id"]
        domain_id = CACHE["domain_ids"][domain]

        url = f"{CF_API}/zones/{zone_id}/dns_records/{domain_id}"
        headers = {
            "X-AUTH-KEY": CF_API_KEY,
            "X-AUTH-EMAIL": CF_EMAIL,
            "CONTENT-TYPE": "application/json",
        }
        payload = {"type": "A", "name": domain, "content": ip}
        print("Updating", domain, "Payload", payload, "URL", url)
        print("Headers", headers)
        r = requests.put(url, headers=headers, json=payload)
        print("Results", r.status_code, r.json())
        print("\n\n")


def main():

    # Collect zone_id if not available in CACHE.json
    cache_save_flag = False
    if not CACHE.get("zone_id", False):
        cache_save_flag = True
        get_zone_id()

    # Check if all domain_id's are found in CACHE.json
    all_found = False
    if CACHE.get("domain_ids", False):
        all_found = all([CACHE["domain_ids"].get(domain, False) for domain in DOMAINS])

    if not all_found:
        cache_save_flag = True
        get_domain_ids()

    # print([CACHE["domain_ids"].get(domain, False) for domain in DOMAINS])

    # print("DumpVar:\n", json.dumps(CACHE, indent=4))

    # Update public ip in cloudflare
    ip = get_public_ip()
    if ip != CACHE.get("public_ip", ""):
        update_cloudflare(ip)
        CACHE["public_ip"] = ip
        cache_save_flag = True
    else:
        print("Not updating Cloudflare - public IP hasn't changed.")

    # Save collected ids in CACHE.json file
    if cache_save_flag:
        save_cache()


if __name__ == "__main__":
    main()
