# nornir3_8021x_conf

Illustrate the following conecepts:
- Set all necessary global Settings for 802.1x on IOS-based Device
- Setting all neccessary interface configurations based on check if description and interface type

Author: nouse4it <github@schlueter-online.net>

## Use Case Description

The script is intended to automatically configure all global commands for enabling 802.1x Authentication.
After that all necessary settings will be done on a per interface basis.
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

Configure global settings as well as per interface settings for 802.1x usage on an access switch device.
