[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/nouse4it/nornir3_8021x_conf)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)

# nornir3_8021x_conf
Automate 802.1x Configuration with Nornir 

Author: nouse4it <github@schlueter-online.net>

nornir3_8021x_conf
Illustrate the following conecepts:
- Set all necessary global Settings for 802.1x on IOS-based Device
- Setting all neccessary interface configurations based on check if description and interface type

## Use Case Description

The script is intended to automatically configure all commands in global configuration mode for enabling 802.1x Authentication.
After that all necessary settings on interface level will be done on a per interface basis.
The dection of which interface are present, an which are acutally access ports, is done by the script.
Only access ports are configured.
All this will done in parallel on multiple devices.

## Installation
Pleae use NORNIR Version 3.0
Following Packtes, Modules and Requirements are needed:
    
    nornir==3.0.0
    nornir-napalm==0.1.1
    nornir-netmiko==0.1.1
    paramiko==2.7.2
    
For more informations see ---> https://github.com/nornir-automation/nornir
Python Version must be at least v3.6.8

## Usage
Please create the neccessary inventory files that nornir works with, and adjust them to your enviroment.
For that please use the following files:

* nornir3_config.yaml     ---> basis config of how nornir should handle connections and where to gather informations
* nornir3_defaults.yaml   ---> can be left empty, but must be present as a file
* nornir3_groups.yaml     ---> is used to group your hosts an provide a plattform info (used for authentication)
* nornir3_hosts.yaml      ---> is used to put in the hosts you want to run the scripts against in yaml format
    
For more help how to setup a inventory please see ---> https://nornir.readthedocs.io/en/latest/tutorial/inventory.html

When you finisched setting up the inventory you can run the script with python3 nornir3_8021x_conf.py
The scripts start an will ask you for the follwing input:
    
* Username for login on the switches
* Password for login on the switches
* Shared Key for the radius authentication
* IP of your first Radius Server
* IP of your second (backup) Radius Server

When you provided this informaations the script run on all the mentioned switches of the nornir3_hosts.yaml file.
The script will set all global commands from the best practice guide for 802.1x of Cisco:
https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_usr_8021x/configuration/xe-3se/3850/sec-user-8021x-xe-3se-3850-book/config-ieee-802x-pba.html#GUID-430BBBAE-CB5D-46F9-80B2-6DF8A5497922

