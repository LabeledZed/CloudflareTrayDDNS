# Cloudflare Dynamic IP Updater

A Python script to automatically update Cloudflare DNS records when your dynamic IP changes. This script is ideal for home servers or any environment where the public IP frequently changes.

## Features
- Automatically fetches the current public IP using the `ipify` service.
- Dynamically retrieves DNS record IDs from Cloudflare, removing manual setup requirements.
- Updates multiple DNS records based on configuration.
- Supports enabling or disabling Cloudflare Proxy (`proxied` option) for each record.
- Runs continuously, checking for IP changes at regular intervals.

## Requirements
- Python 3.7 or higher
- `requests` library

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/cloudflare-dynamic-ip-updater.git
cd cloudflare-dynamic-ip-updater
