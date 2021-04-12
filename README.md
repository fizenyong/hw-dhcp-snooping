# hw-dhcp-snooping
A Python script to enable DHCP snooping for specified vlan by parsing DHCP server mac-address interface setting as the DHCP trusted interface.

## Framework
Script created using:
* Nornir: Inventory management and task multi-threading
* Netmiko: SSH connection to device
* Jinja2: Generating device configuration files
* TextFSM: CLI parsing to structured format
* ntc_template: TextFSM templates
* PyATS Genie: Parsing library (under genie-parser branch)
  * Note: pyATS framework does not support Windows.

## Getting Started
1. Install dependency
```sh
pip install -r requirements.txt
```
2. Add the textfsm template definition to site-package ntc_templates
```sh
LOC=`python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
LOC=${LOC}/ntc_templates/templates
cp ntc_templates/huawei_vrp_display_mac-address_inc.textfsm ${LOC}/huawei_vrp_display_mac-address_inc.textfsm
```
3. Append the textfsm template header to index of site-package ntc_templates
```sh
cat ntc_templates/index | tee -a file.txt ${LOC}/index
```
4. Create logs folder
```sh
mkdir -p logs
```

## How To Use
1. Set up device in `inventory/hosts.yaml`
```yaml
T-LAB-AS-S5730-STACK-01:
  groups:
    - Test
  hostname: 192.168.1.1
```
2. Set up device details in `inventory/groups.yaml`
```yaml
Test:
  username: admin
  password: admin
  platform: huawei
  data:
    # DHCP client vlan
    vlan: 100
    # DHCP server mac-address
    ser_mac: 1c5f-2bf3-870f
```
3. Run the script
```
python ssh-enable-dhcpsnooping
```

## Test
Tested on:
* Huawei S5730-SI of V200R013
* Huawei S5730-SI of V200R019

## Device CLI Logging
Raw CLI stream output stored at logs folder.
To supress logging for certain command, set its Task argument to `severity_level=logging.DEBUG`

## How It Works
1. Establish SSH connection to devices
2. Obtain uplink interface to DHCP server `disp mac-address vlan {vlanid}`
3. Parse the result of DHCP server's mac entry *Learned-From* column
```
MAC Address    VLAN/VSI/BD                       Learned-From        Type      
-------------------------------------------------------------------------------
1c5f-2bf3-870f 31/-/-                            Eth-Trunk1          dynamic   
 
```
4. Deliver the commands rendered of template `inventory/cli-dhcpsnoop-en.j2`
5. Verify the dhcp snooping status state by `disp dhcp snooping configuration`
