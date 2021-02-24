import os
import sys
import requests
import json
import time
import requests

if len(sys.argv) < 3:
    raise Exception("No endpoint specified. ")
endpoint = sys.argv[1]
headers = {
    'Host': sys.argv[2]
}

payload_file = "input.json"
if len(sys.argv) > 3:
    payload_file = sys.argv[3]

with open(payload_file) as file:
    sample_file = json.load(file)

# Split inputs into chunks of size 15 and send them to the predict server
print("Sending explanation requests...")
time_before = time.time()
res = requests.post(endpoint, json=sample_file, headers=headers)

print("TIME TAKEN: ", time.time() - time_before)
print(res)
if not res.ok:
    res.raise_for_status()
print(res.json())