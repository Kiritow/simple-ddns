import os
import sys
import requests


def get_my_ip():
    r = requests.get('http://v4.ident.me')
    return r.content.decode().strip()


if __name__ == "__main__":
    api_token = os.getenv('CF_API_TOKEN')
    zone_name =  sys.argv[1] or os.getenv('CF_ZONE_NAME')
    domain_name = sys.argv[2] or os.getenv('CF_DOMAIN_NAME')

    res = requests.get('https://api.cloudflare.com/client/v4/zones?name={}'.format(zone_name), headers={
        "Authorization": "Bearer {}".format(api_token),
    })
    print(res.content)

    zones = res.json()["result"]
    
    zone_info = [x for x in zones if x['name'] == zone_name][0]
    zone_id = zone_info['id']

    res = requests.get('https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(zone_id), headers={
        "Authorization": "Bearer {}".format(api_token),
    })
    print(res.content)

    domains = res.json()["result"]
    domain_info = [x for x in domains if x['name'] == domain_name][0]
    domain_id = domain_info['id']
    current_ip = domain_info['content']

    client_ip = get_my_ip()
    print("Client ip is: {}".format(get_my_ip()))

    if current_ip == client_ip:
        print('IP matchs with {} ({}), skip patching.'.format(domain_name, current_ip))
        exit(0)

    res = requests.patch('https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
        zone_id, domain_id
    ), headers={
        "Authorization": "Bearer {}".format(api_token),
    }, json={
        'content': client_ip,
    })
    print(res.content)

    print('Successfully updated {} from {} to {}'.format(domain_name, current_ip, client_ip))
