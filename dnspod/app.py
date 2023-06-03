import os
import sys
from tencentcloud.common import credential
from tencentcloud.dnspod.v20210323 import dnspod_client, models
import requests


SEC_ID = os.getenv('SEC_ID')
SEC_KEY = os.getenv('SEC_KEY')
DOMAIN_NAME = os.getenv('DOMAIN_NAME')


cred = credential.Credential(SEC_ID, SEC_KEY)
client = dnspod_client.DnspodClient(cred, '')


def get_dnspod_dc_record(dc_name):
    dns_prefix = '{}-dc'.format(dc_name)

    req = models.DescribeRecordListRequest()
    req.Domain = DOMAIN_NAME

    resp = client.DescribeRecordList(req)
    for record in resp.RecordList:
        if record.Name == dns_prefix:
            return record

    return None


def get_my_ip():
    r = requests.get('http://v4.ident.me')
    return r.content.decode().strip()


def update_dnspod_dc_record(dc_name, ipv4_address):
    dns_prefix = '{}-dc'.format(dc_name)
    real_dns_name = '{}.{}'.format(dns_prefix, DOMAIN_NAME)

    record = get_dnspod_dc_record(dc_name)
    if record.Value == ipv4_address:
        print('IP matchs with {} ({}), skip patching.'.format(real_dns_name, ipv4_address))
        return

    req = models.ModifyRecordRequest()
    req.Domain = DOMAIN_NAME
    req.RecordType = record.Type
    req.RecordLine = record.Line
    req.Value = ipv4_address
    req.RecordId = record.RecordId
    # req.DomainId
    req.SubDomain = record.Name
    req.RecordLineId = record.LineId
    req.MX = record.MX
    req.TTL = record.TTL
    req.Weight = record.Weight
    req.Status = record.Status

    print(req.to_json_string())

    resp = client.ModifyRecord(req)
    print(resp.to_json_string())
    print('Successfully updated {} from {} to {}'.format(real_dns_name, record.Value, ipv4_address))


if __name__ == '__main__':
    dc_name = sys.argv[1]

    client_ip = get_my_ip()
    print("Client IP is: {}".format(get_my_ip()))
    
    update_dnspod_dc_record(dc_name, client_ip)
