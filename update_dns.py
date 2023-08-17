
import xmlrpc.client
import requests
import json
import os

# https://appendix.interworx.com/current/api/index.html

WEBXSERVER_ADDR = "your webx server address here"

key_file = ".key"
domain = "retrozelda.com" # the domain account
controller = "/siteworx/dns"

zones_to_focus = ['pornhub.fit'] # a domain under the main master
hosts_to_focus =[ # the subdomains we want to update to point to this machine
    #'test.pornhub.fit', 
]

def run_api(email, password, domain, controller, action, input_params):
    client = xmlrpc.client.ServerProxy(f'{WEBXSERVER_ADDR}:2443/xmlrpc')
    response = client.iworx.route({'email': email, 'password': password, 'domain': domain}, controller, action, input_params)
    return response

def get_public_ipv4():
    try:
        response = requests.get('https://api.ipify.org/?format=json')
        data = response.json()
        return data['ip']
    except Exception as e:
        print("Error:", e)
        return None
    
def get_public_ipv6():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        data = response.json()
        return data['ip']
    except Exception as e:
        print("Error obtaining IPv4:", e)
        return None

def save_ip_to_file(ip, file_name):
    try:
        with open(file_name, 'w') as file:
            file.write(ip)
        print(f"IP address saved to file \"{file_name}\".")
    except Exception as e:
        print("Error saving IP to file \"{file_name}\":", e)

def read_ip_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return file.readline().strip()
    except Exception as e:
        print("Error reading IP from file \"{file_name}\":", e)
        return None
    
def is_ip_changed(current_ipv4_address):
    saved_ipv4_address = read_ip_from_file(".ip_cache")
    if saved_ipv4_address and saved_ipv4_address == current_ipv4_address:
        print("IP address has not changed:", current_ipv4_address)
        return False
    else:
        print("IP address has changed. New IP:", current_ipv4_address)
        save_ip_to_file(current_ipv4_address, ".ip_cache")
        return True
    
def main():

    if not os.path.exists(key_file):
        print(f"missing \"{key_file}\" file")

    email = ""
    password = ""
    with open(key_file, 'r') as json_file:
        json_data = json.load(json_file)
        if 'email' in json_data and 'password' in json_data:
            email = json_data['email']
            password = json_data['password']
        else:
            print("Key file is incorrect.")
            return

    new_ip = get_public_ipv4()
    if new_ip is None:
        print("Failed to get public IP.  Is the network connected to the internet?")
        return
    
    if not is_ip_changed(new_ip):
        return
    
    print("Scanning our zones...")
    action = "listZones"
    input_params = {
        #'record_id': domain
    }
    zones_response = run_api(email, password, domain, controller, action, input_params)
    if zones_response['status'] != 0:
        print(f"listZones returned error {zones_response['status']}: {zones_response['payload']}")
        return
    
    print("Scanning each zone for our domains...")
    zone_ids = []
    for zone in zones_response['payload']:
        if any(zone_check == zone['domain'] for zone_check in zones_to_focus):
            print(f"Found domain: {zone['domain']} with zone_id {zone['zone_id']}")
            zone_ids.append(zone['zone_id'])
            
    for zone_id in zone_ids:
        action = "queryDnsRecords"
        input_params = {
            'zone_id': zone_id
        }

        print(f"Querying DNS for zone_id {zone_id}")
        dns_response = run_api(email, password, domain, controller, action, input_params)
        if dns_response['status'] != 0:
            print(f"queryDnsRecords for zone_id {zone_id} returned error {dns_response['status']}: {dns_response['payload']}")
            continue

        record_ids = []
        for dns_record in dns_response['payload']:
            if dns_record['type'] != 'A':
                continue

            if any(host_check == dns_record['host'] for host_check in hosts_to_focus):
                if dns_record['target'] != new_ip:
                    print(f"Found host \"{dns_record['host']}\" for zone_id {zone_id} thats needs updated. record_id {dns_record['record_id']}")
                    record_ids.append(dns_record['record_id'])
        
        if len(record_ids) == 0:
            print(f"No records that need upodated were found for zone_id {zone_id}")

        for record_id in record_ids:

            # verify we can edit this record
            action = "queryEditA"
            input_params = {
                'record_id': record_id
            }

            print(f"Verifying record_id {dns_record['record_id']} for zone_id {zone_id}")
            edit_query_response = run_api(email, password, domain, controller, action, input_params)
            if edit_query_response['status'] != 0:
                print(f"queryEditA for record_id {record_id} returned error {edit_query_response['status']}: {edit_query_response['payload']}")
                continue
            if edit_query_response['payload']['ipaddress'] == new_ip:
                print(f"unnessisary edit for record_id {dns_record['record_id']} for zone_id {zone_id}")
                continue

            # we should be valid to change.  do it
            action = "editA"
            input_params = {
                'record_id': record_id,
                'ipaddress': new_ip,
            }
            print(f"Updating address for record_id {dns_record['record_id']} for zone_id {zone_id}")
            edit_response = run_api(email, password, domain, controller, action, input_params)
            if edit_response['status'] != 0:
                print(f"editA for record_id {record_id} returned error {edit_response['status']}: {edit_response['payload']}")
                continue
            print(f"Updating address for record_id {dns_record['record_id']} for zone_id {zone_id} success.")


if __name__ == "__main__":
    main()
