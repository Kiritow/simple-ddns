import CloudFlare
import requests
import os
import sys


CF_API_TOKEN = os.getenv('CF_API_TOKEN')
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
HTTP_PROXY = os.getenv('http_proxy')


def get_my_ip():
    r = requests.get('https://v4.ident.me', proxies={
        'https': HTTP_PROXY,
    } if HTTP_PROXY else None)
    return r.content.decode().strip()


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
        return

    cf.zones.dns_records.put(zone_id, dns_record['id'], data={
        'name': full_dnsname,
        'type': 'A',
        'content': ipv4_address,
        'proxied': dns_record['proxied']
    })
    print('Successfully updated {} from {} to {}'.format(full_dnsname, dns_record['content'], ipv4_address))


if __name__ == '__main__':
    dc_name = sys.argv[1]
    client_ip = get_my_ip()
    print("Client IP is: {}".format(get_my_ip()))

    check_and_update_cf_dc_record(dc_name, client_ip)
