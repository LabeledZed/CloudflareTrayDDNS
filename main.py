import os
from pystray import MenuItem as item
import pystray
from PIL import Image as pilmg
from contextlib import redirect_stdout
import requests
import json
import time
from threading import Thread
import sys as system
from tkinter.messagebox import showerror

run = True

if getattr(system, 'frozen', False):
    truepath = system._MEIPASS
    path = os.path.abspath(os.path.join(system.executable, os.pardir))
else:
    truepath = os.getcwd()
    path = truepath


# Load configuration from config.json
def load_config():
    try:
        with open(os.path.join(path, "config.json"), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        showerror("Error", "config.json not found. Please create the configuration file.")
        exitapp()
    except json.JSONDecodeError:
        showerror("Error", "Invalid JSON format in config.json.")
        exitapp()


# Get the current public IP address
def get_current_ip():
    try:
        ip = requests.get('https://api.ipify.org').text
        print(f"Current IP: {ip}")
        return ip
    except requests.RequestException as e:
        print(f"Error getting IP address: {e}")
        return None


# Get the DNS record ID for a given record name
def get_record_id(api_token, zone_id, record_name):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {"name": record_name}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        records = response.json().get("result", [])
        if records:
            record_id = records[0]["id"]
            print(f"Found Record ID for {record_name}: {record_id}")
            return record_id
        else:
            print(f"Record not found: {record_name}")
            return None
    except requests.RequestException as e:
        print(f"Error getting record ID for {record_name}: {e}")
        if e.response:
            print(f"Response details: {e.response.text}")
        return None


# Update the DNS record with the new IP address
def update_record(api_token, zone_id, record_id, record_name, ip_address, proxied):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": record_name,
        "content": ip_address,
        "ttl": 1,  # Auto TTL
        "proxied": proxied
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully updated {record_name} to IP {ip_address} with proxied={proxied}.")
    except requests.RequestException as e:
        print(f"Error updating record {record_name}: {e}")
        if e.response:
            print(f"Response details: {e.response.text}")


# Main function to check IP and update records
def main():
    global run
    while run:
        with redirect_stdout(open(os.path.join(path, 'debug.log'), 'w')):
            config = load_config()
            current_ip = get_current_ip()

            if current_ip is None:
                print("Failed to retrieve the current IP. Skipping update.")
                return

            for record in config["records"]:
                api_token = record["api_token"]
                zone_id = record["zone_id"]
                record_name = record["record_name"]
                proxied = record.get("proxied", False)  # Default to False if not specified

                print(f"Processing record: {record_name}")

                # Get the DNS record ID from Cloudflare API
                record_id = get_record_id(api_token, zone_id, record_name)

                if record_id:
                    update_record(api_token, zone_id, record_id, record_name, current_ip, proxied)
        i = 0
        while i < 6000 and run:
            time.sleep(0.1)
            i = i + 1


def exitapp():
    global run
    run = False
    icon.stop()
    time.sleep(0.1)
    system.exit()


if not os.path.isfile(os.path.join(path, 'debug.log')):
    open(os.path.join(path, 'debug.log'), 'x')
Thread(target=main).start()
image = pilmg.open(os.path.join(truepath, "ico\\ddns.ico"))
menu = (item('Quit', exitapp),)
icon = pystray.Icon("name", image, "Cloudflare DDNS", menu)
icon.run()
