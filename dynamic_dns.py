from dotenv import load_dotenv
import os
import re
import requests
import sys

load_dotenv()

if len(sys.argv) != 2:
  print("Usage: python dynamic_dns.py <nb_hostnames>")
  exit(1)

try:
  nb_hostnames = int(sys.argv[1])
except ValueError:
  print("Error: nb_hostnames must be an integer")
  exit(1)

if nb_hostnames < 1:
  print("Error: nb_hostnames must be greater than zero")
  exit(1)

ip_regexp = re.compile(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")

current_ip = os.popen("curl -s ifconfig.me").readline()

if not ip_regexp.match(current_ip):
  print(f"Error: failed to fetch IP address ({current_ip})")
  exit(1)

print(f"Current IP address is {current_ip}")

dirname = os.path.dirname(__file__)
ip_address_filename = os.path.join(dirname, "ip_address.txt")

try:
  with open(ip_address_filename, "r") as f:
    previous_ip = f.read()
    print(f"Previous IP address is {previous_ip}")

    if current_ip == previous_ip:
      print("IP address has not changed, exiting")
      exit(0)
    else:
      print("IP address has changed")
except IOError:
  print("Previous IP address not found")

for i in range(1, nb_hostnames + 1):
  host = os.environ.get(f"HOST_{i}")
  domain = os.environ.get(f"DOMAIN_{i}")
  password = os.environ.get(f"PASSWORD_{i}")

  if host is None or domain is None or password is None:
    print(f"Error: missing configs for hostname #{i}")
    exit(1)

  url = f"https://dynamicdns.park-your-domain.com/"
  url += f"update?host={host}&domain={domain}&password={password}&ip={current_ip}"

  headers = {
    "Authorization": "Basic base64-encoded-auth-string",
    "User-Agent": "Chrome/112.0 fytpet@gmail.com"
  }

  print(f"Updating DNS for hostname #{i}")
  response = requests.get(url, headers=headers)
  print(f"Response: {response.text}")

with open("./ip_address.txt", "w") as f:
  f.write(current_ip)
  print("Current IP address saved")
