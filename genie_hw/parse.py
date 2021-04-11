try:
    from genie.conf.base import Device
    from genie_hw.show_fdb import ShowMacAddressTable
    from genie_hw.show_dhcp_config import ShowDhcpConf

    GENIE_INSTALLED = True
except ImportError:
    GENIE_INSTALLED = False


def parse_genie(platform, command, raw_output):
    if not GENIE_INSTALLED:
        raise ValueError("Genie parser failed to load")

    device = Device("new_device", os=platform)

    if command == "disp mac":
        parser = ShowMacAddressTable(device=device)
    elif command == "disp dhcp":
        parser = ShowDhcpConf(device=device)

    parser.output = raw_output

    return parser.parse()