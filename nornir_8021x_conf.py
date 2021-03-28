#!/usr/bin/python

"""
Category: Python Nornig Config Script
Author: nouse4it <github@schlueter-online.net>

nornir_8021x_complete.py
Illustrate the following conecepts:
- Set all necessary global Settings for 802.1x on IOS-based Device
- Setting all neccessary interface configurations based on check if description and interface type
"""

__author__ = "nouse4it"
__author_email__ = "github@schlueter-online.net"
__copyright__ = "Copyright (c) 2020 nouse4it"

# Importing all needed Modules
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko import netmiko_send_command, netmiko_send_config
from nornir.core.filter import F
import getpass

nr = InitNornir(config_file="/home/nouse4it/Scripts/Nornir/config_files/nornir3_config.yaml")

access_user = input('Enter Access Username: ') # Enter Username for Access Switch
access_password = getpass.getpass(prompt ="Access Switch password: ") # Enter password for Device in Access Group in Hosts.yaml

nr.inventory.groups['a'].username = access_user # set Username for Access Group
nr.inventory.groups['a'].password = access_password # set password for Core Group

shared_key = input('Enter Radius Shared Key for location: ')
radius_ip_1 = input('Enter Radius Server 1 IP Address: ')
radius_ip_2 = input('Enter Radius Server 2 IP Address: ')
#----------------------------------------------------------------------------------------------------------------------
def global_config(task):
    r = task.run(task=netmiko_send_config, name='Set Global dot1x Settings', config_commands=[
        "aaa authentication dot1x default group radius",
        "aaa authorization network default group radius",
        "aaa accounting dot1x default start-stop group radius",
        # für CoA
        "aaa server radius dynamic-author",
        "client {} server-key 0 {}".format(radius_ip_1, shared_key),
        "client {} server-key 0 {}".format(radius_ip_2, shared_key),
        "ip device tracking",
        # Probe Delay to 10 seconds to work around the DHCP duplicate IP problem starting with Windows 7
        "ip device tracking probe delay 10",
        # Mechanism to prevent problems when EAP logoff does not work properly. 
        # E.g. PC behind phone moves to another switch port, the switch then changes the MAC session.  
        "authentication mac-move permit",
        # Enable 802.1x
        "dot1x system-auth-control",
        # Addtional Information Gathering for RADIUS Server
        "radius-server attribute 6 on-for-login-auth",
        "radius-server attribute 8 include-in-access-req",
        "radius-server attribute 25 access-request include",
        "radius-server vsa send accounting",
        "radius-server vsa send authentication",
        "radius server {}".format(radius_ip_1),
        "address ipv4 {}".format(radius_ip_1),
        "key 0 {}".format(shared_key),
        "radius server {}".format(radius_ip_2)
        "address ipv4 {}".format(radius_ip_2)
        "key 0 {}".format(shared_key),
        # Better behavior in case of error to avoid flapping the dead radius is set to dead for 15min
        "radius-server dead-criteria time 10 tries 3",
        "radius-server deadtime 15"]
        ) 
#----------------------------------------------------------------------------------------------------------------------
def interface_config(task):
    r = task.run(task=netmiko_send_command,name='Gather Interface Informations', command_string="sh interfaces switchport", use_genie=True)
    intf_dict = r.result
    intf_list = []
    for intf_id,intf_info in intf_dict.items():
        if intf_info['switchport_mode'] == 'static access':
            intf_list.append(intf_id)

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
            "authentication host-mode multi-auth",
            "authentication open",
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

#==============================================================================
# ---- Main: Run Commands
#==============================================================================  

results_global = nr.run(task=global_config)
results_intf = nr.run(task=interface_config)

print_result(results_global)
print_result(results_intf)

write_mem = nr.run(task=netmiko_send_command, command_string="write mem", use_genie=True)
