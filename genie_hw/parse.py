try:
    from genie.conf.base import Device
    from genie_hw.show_fdb import ShowMacAddressTable
    from genie_hw.show_dhcp_config import ShowDhcpConf
    from genie_hw.show_arp import ShowArp

except ImportError:
    raise ValueError("Genie parser failed to load")


def parse_genie(platform, command, raw_output):

    device = Device("new_device", os=platform)

    if command == "disp mac":
        parser = ShowMacAddressTable(device=device)
    elif command == "disp dhcp":
        parser = ShowDhcpConf(device=device)
    elif command == "disp arp":
        parser = ShowArp(device=device)

    parser.output = raw_output

    return parser.parse()