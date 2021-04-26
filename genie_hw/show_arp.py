from genie.libs.parser.iosxe.show_arp import ShowArp as ShowArp_ios
from genie.libs.parser.utils.common import Common
import re


class ShowArp(ShowArp_ios):
    """ Parser for display arp """

    """
    IP ADDRESS      MAC ADDRESS     EXPIRE(M) TYPE        INTERFACE   VPN-INSTANCE
                                            VLAN/CEVLAN PVC
    ----------------------------------------------------------------------------------------
    10.255.100.18   44a1-9169-fd3c            I -         Eth-Trunk2       
    10.255.100.17   44a1-9169-feac  10        D-0         Eth-Trunk2       
    ----------------------------------------------------------------------------------------
    Total:115         Dynamic:95       Static:0    Interface:20    Remote:0
    Redirect:0
    """

    def cli(self, output=None):
        # Get output from self.output set in Nornir task
        out = self.output

        # Initial return dictionary
        ret_dict = {}

        # 10.255.100.18   44a1-9169-fd3c            I -         Eth-Trunk2
        # 10.255.100.17   44a1-9169-feac  10        D-0         Eth-Trunk2
        p1 = re.compile(
            r"(?P<address>[\d\.]+) +(?P<mac>[\w\-]+) +(?P<age>[\d]+)? +(?P<origin>[IDS])[\-\s][\-\d] +(?P<interface>[\w\.\-\/]+)"
        )

        for line in out.splitlines():
            line = line.strip()

            # 10.255.100.18   44a1-9169-fd3c            I -         Eth-Trunk2
            # 10.255.100.17   44a1-9169-feac  10        D-0         Eth-Trunk2
            m = p1.match(line)
            if m:
                group = m.groupdict()
                address = group["address"]
                interface = group["interface"]
                if interface:
                    final_dict = (
                        ret_dict.setdefault("interfaces", {})
                        .setdefault(interface, {})
                        .setdefault("ipv4", {})
                        .setdefault("neighbors", {})
                        .setdefault(address, {})
                    )

                    final_dict["ip"] = address
                    final_dict["link_layer_address"] = group["mac"]
                    final_dict["type"] = ""
                    if group["origin"] == "D":
                        final_dict["origin"] = "dymanic"
                    elif group["origin"] == "I":
                        final_dict["origin"] = "interface"
                    else:
                        final_dict["origin"] = "static"

                final_dict["age"] = group["age"] if group["age"] else ""
                final_dict["protocol"] = ""
                continue

        return ret_dict