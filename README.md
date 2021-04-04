# hw-dhcp-snooping
Script using Nornir Framework and Netmiko SSH to enable dhcp snooping for Huawei Sx7 switch

## Introduction
Automation script to auto configure DHCP snooping for specified vlan by parsing current DHCP server mac-address interface as DHCP trusted interface.

## Framework
Script created using:
* Nornir: Inventory management and task automation
* Netmiko: SSH connection
* ntc_template: CLI output parsing using Textfsm
* Jinja2: CLI templating

## Prerequisites
Add the textfsm template and index (under ntc_templates folder) to site-package ntc_templates

## Running
```
python hw-dhcp-snooping
```
