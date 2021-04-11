from genie.libs.parser.iosxe.show_fdb import ShowMacAddressTable as ShowMacAddressTable_ios
from genie.libs.parser.utils.common import Common
import re


class ShowMacAddressTable(ShowMacAddressTable_ios):
    """Overide Genie ios Parser implementation for Huawei display mac address-table"""

    """
    Output Sample:
    ------------------------------------------------------------------------------- 
    MAC Address          VLAN/VSI/BD                 Learned-From        Type       
    -------------------------------------------------------------------------------
    0000-0000-0033       100/-/-                     GE0/0/1             dynamic 
    0000-0000-0001       200/-/-                     GE0/0/2             static 
    -------------------------------------------------------------------------------
    """

    def cli(self, output=None):
        # Get output from self.output set in Nornir task
        out = self.output

        # initial return dictionary
        ret_dict = mac_dict = {}
        entry_type = entry = learn = age = ""

        # Total items displayed = 2
        p1 = re.compile(r"^Total +items +displayed += +(?P<val>\d+)$")

        # 0000-0000-0033       100/-/-                     GE0/0/1             dynamic
        # 0000-0000-0001       200/-/-                     GE0/0/2             static
        p2 = re.compile(
            r"^(?P<mac>[\w-]+) +(?P<vlan>[\d]+)/[\d-]+/[\d-]+ +(?P<intfs>\S+|[^\s]+\s[^\s]+) +(?P<entry_type>\w+)$"
        )

        for line in out.splitlines():
            line = line.strip()

            # Total items displayed = 2
            m = p1.match(line)
            if m:
                ret_dict.update({"total_mac_addresses": int(m.groupdict()["val"])})
                continue

            # 0000-0000-0033       100/-/-                     GE0/0/1             dynamic
            # 0000-0000-0001       200/-/-                     GE0/0/2             static
            m = p2.match(line)
            if m:
                group = m.groupdict()
                mac = group["mac"]
                vlan = (
                    int(group["vlan"])
                    if re.search("\d+", group["vlan"])
                    else group["vlan"].lower()
                )
                intfs = group["intfs"].strip()
                vlan_dict = (
                    ret_dict.setdefault("mac_table", {})
                    .setdefault("vlans", {})
                    .setdefault(str(vlan), {})
                )
                vlan_dict["vlan"] = vlan
                mac_dict = vlan_dict.setdefault("mac_addresses", {}).setdefault(mac, {})
                mac_dict.update({"mac_address": mac})

                if "drop" in intfs.lower():
                    drop_dict = mac_dict.setdefault("drop", {})
                    drop_dict.update({"drop": True})
                    drop_dict.update({"entry_type": group["entry_type"].lower()})
                    continue

                for intf in intfs.replace(" ", ",").split(","):
                    intf = Common.convert_intf_name(intf)
                    intf_dict = mac_dict.setdefault("interfaces", {}).setdefault(
                        intf, {}
                    )
                    intf_dict.update({"interface": intf})
                    entry_type = group["entry_type"].lower()
                    intf_dict.update({"entry_type": entry_type})

                continue

        return ret_dict