import requests
import json
import time

# Load configuration from config.json
def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: config.json not found. Please create the configuration file.")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in config.json.")
        exit()

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

if __name__ == "__main__":
    print("---Starting Cloudflare Dynamic IP Updater---\n")
    while True:
        main()
        time.sleep(600)  # Check every 10 minutes (600 seconds)
