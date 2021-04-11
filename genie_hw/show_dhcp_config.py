"""display dhcp snooping configuration
"""
"""Output Sample:
dhcp snooping enable
#
vlan 3
 dhcp snooping enable
 dhcp snooping check dhcp-giaddr enable
#
vlan 37
 dhcp snooping enable
#
"""
import re

from genie.metaparser import MetaParser
from genie.metaparser.util.schemaengine import (
    Schema,
    Any,
    Optional,
    Or,
    And,
    Default,
    Use,
)

# import parser utils
from genie.libs.parser.utils.common import Common


class ShowDhcpConfSchema(MetaParser):
    """Schema for show dhcp snooping configuration"""

    schema = {
        "enabled": bool,
        Optional("vlans"): {
            Any(): {"vlan": str, "enabled": bool, Optional("giaddr"): bool}
        },
    }


class ShowDhcpConf(ShowDhcpConfSchema):
    """Parser for show dhcp snooping configuration"""

    cli_command = "display dhcp snooping configuration"

    def cli(self, output=None):
        # Get output from self.output set in Nornir task
        out = self.output

        # initial return dictionary
        ret_dict = {}

        # initial regexp pattern
        p1 = re.compile(r"^dhcp +snooping +enable$")
        p2 = re.compile(r"^vlan +(?P<vlan_id>\d+)$")
        p3 = re.compile(r"^dhcp +snooping +check +dhcp-giaddr +enable$")

        for line in out.splitlines():
            line = line.strip()

            # dhcp snooping enable
            m = p1.match(line)
            if m:
                ret_dict["enabled"] = True
                continue

            # vlan 3
            m = p2.match(line)
            if m:
                vlan = m.groupdict()["vlan_id"]
                vlan_dict = ret_dict.setdefault("vlans", {}).setdefault(vlan, {})
                vlan_dict["vlan"] = vlan
                vlan_dict["enabled"] = True
                continue

            # dhcp snooping check dhcp-giaddr enable
            m = p3.match(line)
            if m:
                vlan_dict["giaddr"] = True
                continue

        return ret_dict
