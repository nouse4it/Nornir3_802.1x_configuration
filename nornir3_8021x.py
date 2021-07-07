#!/usr/bin/python

"""
Category: Python Nornig Config Script
Author: NoUse4IT <github@schlueter-online.net>

nornir_8021x_complete.py
Illustrate the following concepts:
- Set all necessary global Settings for 802.1x on IOS-based Device
- Setting all neccessary interface configurations based on check if description and interface type
- Add the Device to ISE with all secrets and needed groups
"""

__author__ = "nouse4it"
__author_email__ = "github@schlueter-online.net"
__copyright__ = "Copyright (c) 2021 nouse4it"

# Importing all needed Modules
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir.core.filter import F
import json
import pprint
import requests
import urllib3
import sys
import os
import socket
import getpass

urllib3.disable_warnings()

nr = InitNornir(config_file="/home/nouse4it/scripts/nornir/config_files/nornir3_config.yaml")

nr.inventory.groups['a'].username = os.getenv("USER") # set Username
nr.inventory.groups['a'].password = os.getenv("PW") # set password

hosts = nr.filter(dot1x="yes") # use only hosts where "data: dot1x: yes" is set in Host Inventory File!

host_list = [] # List for all Hosts that should be added to ISE later

radius_key = getpass.getpass('Enter Radius Shared Key for location: ')
tacacs_key = getpass.getpass('Enter TACACS Shared Key for location: ')
snmp_community = getpass.getpass('Enter SNMP Community: ')
ise_api_user = input('Enter ISE API User: ')
ise_api_ip = input('Enter ISE API IP: ')
ise_api_pwd = getpass.getpass('Enter ISE API PW: ')
radius_ip_1 = input('Enter first Radius IP: ')
radius_ip_2 = input('Enter second Radius IP: ')

#----------------------------------------------------------------------------------------------------------------------
def global_config(task):
    r = task.run(netmiko_send_config, name='Set Global dot1x Settings', config_commands=[
        "aaa authentication dot1x default group radius",
        "aaa authorization network default group radius",
        "aaa accounting dot1x default start-stop group radius",
        "aaa server radius dynamic-author",
        "client " + radius_ip_1 + "server-key 0 " + radius_key,
        "client " + radius_ip_2 + "server-key 0 " + radius_key,
        "ip device tracking",
        "ip device tracking probe delay 10",
        "authentication mac-move permit",
        "dot1x system-auth-control",
        "radius-server attribute 6 on-for-login-auth",
        "radius-server attribute 8 include-in-access-req",
        "radius-server attribute 25 access-request include",
        "radius-server vsa send accounting",
        "radius-server vsa send authentication",
        "radius server Radius 1",
        "address ipv4 " + radius_ip_1,
        "key 0 " + radius_key,
        "radius server Radius 2",
        "address ipv4 " + radius_ip_2,
        "key 0 " + radius_key,
        "radius-server dead-criteria time 10 tries 3",
        "radius-server deadtime 15"]
        ) 
#----------------------------------------------------------------------------------------------------------------------
def interface_config(task):
    r = task.run(task=netmiko_send_command, command_string="sh interfaces switchport", use_genie=True)
    intf_dict = r.result
    intf_list = []
    for intf_id,intf_info in intf_dict.items():
        if intf_info['switchport_mode'] == 'static access':
            intf_list.append(intf_id)
    
    print('The following Interfaces will be configured:')
    print('--------------------------------------------')
    print(intf_list)

    for intf_id in intf_list:
            intf_config = task.run(netmiko_send_config,name="Set Interface command for " + intf_id ,config_commands=[
            "interface " + intf_id,
            "no switchport port-security mac-address sticky",
            "no switchport port-security violation restrict",        
            "no switchport port-security maximum",
            "no switchport port-security",
            "spanning-tree bpduguard enable",
            "spanning-tree portfast edge",
            "authentication control-direction in",
            "authentication event fail action next-method",
            "authentication event server dead action authorize voice",
            "authentication event server alive action reinitialize",
            "no authentication host-mode multi-auth",
            "authentication host-mode multi-domain",
            "no authentication open",
            "authentication order mab dot1x",
            "authentication priority dot1x mab",
            "authentication port-control auto",
            "authentication periodic",
            "authentication timer reauthenticate server",
            "authentication timer restart 14400",
            "authentication violation restrict",
            "mab",
            "dot1x pae authenticator",
            "dot1x timeout tx-period 8",
            "no switchport port-security maximum"]
            )

#----------------------------------------------------------------------------------------------------------------------
def ise_config(hostname,tacacsSharedSecret,location,building,switchtype,ip,radiusSharedSecret,ise_api_ip,ise_api_user,ise_api_pwd):
    body = {
        "NetworkDevice": {
            "name": hostname,
            "authenticationSettings": {
                "radiusSharedSecret": radiusSharedSecret,
                "enableKeyWrap": "false",
                "keyEncryptionKey": "1234567890123456",
                "keyInputFormat": "ASCII"
            },
            "snmpsettings": {
                "version": "TWO_C",
                "roCommunity": snmp_community,
                "pollingInterval": "28800",
                "linkTrapQuery": "true",
                "macTrapQuery": "true",
                "originatingPolicyServicesNode": "Auto"
            },
            "tacacsSettings": {
                "sharedSecret": tacacsSharedSecret,
                "connectModeOptions": "ON_LEGACY"
            },
            "profileName": "Cisco",
            "coaPort": "1700",
            "NetworkDeviceIPList": [
                {
                    "ipaddress": ip,
                    "mask": "32"
                }
            ],
            "NetworkDeviceGroupList": [
                "Location#All Locations#{}#{}".format(location,building),
                "IPSEC#Is IPSEC Device#No",
                "Device Type#All Device Types#Switch#{}".format(switchtype)
            ]
        }
    }

    update_json = json.dumps(body)
    update_device(hostname,ise_api_ip,ise_api_user,ise_api_pwd,update_json)

#------------------------------------------------------------------------------
# Send the privious generated JSON to ISE
def update_device(hostname,ise_api_ip,ise_api_user,ise_api_pwd,json):
    url = 'https://{}:9060/ers/config/networkdevice/name/{}'.format(ise_api_ip, hostname.upper())
    headers = {'ACCEPT': 'application/json','content-type': 'application/json'}
    req = requests.put(url, headers=headers, auth=(ise_api_user, ise_api_pwd), data=json, verify=False)
    print(req.text)
    return

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

results_global = hosts.run(task=global_config)
results_intf = hosts.run(task=interface_config)

print_result(results_global)
print_result(results_intf)

write_mem = hosts.run(task=netmiko_send_command, command_string="write mem", use_genie=True)

# Add all Hosts that Nornir worked on to list for later adding them to ISE via API
for dev in hosts.inventory.hosts.items():
    host_list.append(dev[0])

# Hostname gives every value i need seperate by '-' so i cut the needed informations out of the hostname string
for host in host_list:
    location = host[:3].upper()
    building = host[8:10]
    swt = host[6:7]
    if swt == "a":
        switchtype = "Access Switch"
    ip = socket.gethostbyname(host) # DNS Lookup for getting the IP of the Switch
    ise_config(host,tacacs_key,location,building,switchtype,ip,radius_key,ise_api_ip,ise_api_user,ise_api_pwd) 
