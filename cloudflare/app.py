import CloudFlare
import requests
import os
import sys
import traceback


CF_API_TOKEN = os.getenv('CF_API_TOKEN')
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
CHECK_HTTP_PROXY = os.getenv('CHECK_HTTP_PROXY')
REPORT_LINK = os.getenv('REPORT_LINK')


def get_my_ip():
    r = requests.get('https://v4.ident.me', proxies={
        'https': CHECK_HTTP_PROXY,
    } if CHECK_HTTP_PROXY else None)
    return r.content.decode().strip()


def report_status(dc_name, new_ip, old_ip):
    try:
        r = requests.post(REPORT_LINK, json={
            "dc": dc_name, "new": new_ip, "old": old_ip,
        }, timeout=5)
        print(r.content)
    except Exception:
        print(traceback.format_exc())


def check_and_update_cf_dc_record(dc_name, ipv4_address):
    dns_prefix = '{}-dc'.format(dc_name)
    full_dnsname = '{}.{}'.format(dns_prefix, DOMAIN_NAME)

    cf = CloudFlare.CloudFlare(token=CF_API_TOKEN)
    zones = cf.zones.get(params={'name': DOMAIN_NAME})

    zone_id = zones[0]['id']

    records = cf.zones.dns_records.get(zone_id, params={
        'name': full_dnsname,
        'match': 'all',
        'type': 'A',
    })

    dns_record = records[0]
    if dns_record['content'] == ipv4_address:
        print('IP matchs with {} ({}), skip patching.'.format(full_dnsname, ipv4_address))
        return ipv4_address, ipv4_address

    cf.zones.dns_records.put(zone_id, dns_record['id'], data={
        'name': full_dnsname,
        'type': 'A',
        'content': ipv4_address,
        'proxied': dns_record['proxied']
    })
    print('Successfully updated {} from {} to {}'.format(full_dnsname, dns_record['content'], ipv4_address))

    return ipv4_address, dns_record['content']


if __name__ == '__main__':
    dc_name = sys.argv[1]
    client_ip = get_my_ip()
    print("Client IP is: {}".format(get_my_ip()))

    new_ip, old_ip = check_and_update_cf_dc_record(dc_name, client_ip)
    
    if REPORT_LINK:
        report_status(dc_name, new_ip, old_ip)
