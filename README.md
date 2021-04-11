# hw-dhcp-snooping
Python script to enable DHCP snooping for specified vlan by setting DHCP server mac-address interface as DHCP trusted interface.

## Framework
Script created using:
* Nornir: Inventory management and task automation
* Netmiko: SSH connection
* ntc_template: CLI output parsing using Textfsm
* Jinja2: CLI templating
* PyATS Genie: Parsing library (under genie-parser branch) 

## Prerequisites
Install dependency
```
pip install -r requirements.txt
```

Add the textfsm template definition to site-package ntc_templates
```
LOC=`python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
LOC=${LOC}/ntc_templates/templates
cp ntc_templates/huawei_vrp_display_mac-address_inc.textfsm ${LOC}/huawei_vrp_display_mac-address_inc.textfsm
```

Append the textfsm template header to index of site-package ntc_templates
```
cat ntc_templates/index | tee -a file.txt ${LOC}/index
```
Create logs folder (for storing raw output result)
```
mkdir logs
```

## Launch
```
python ssh-enable-dhcpsnooping
```
## Test
Tested running on:
* Huawei S5730-SI switch of V200R013

## Logging
Raw CLI stream output at logs folder
To supress logging, set Task to *severity_level=logging.DEBUG*

## Functionalities
1. Get switch mac-address table
2. Parse table for interface information
3. Generate config
4. Deliver config
5. Verify after config
