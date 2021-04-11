from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_title, print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_jinja2.plugins.tasks import template_file
from nornir.core.filter import F
from genie_hw.parse import parse_genie
import logging


def result_content(task: Task) -> str:
    content = []

    for r in task.results:
        if r.severity_level < 20:  # Skip if logging.DEBUG
            continue
        content.append(f"<{r.name}>")
        content.append(r.result)
        content.append("</end>\n")
    return "\n".join(content)


def get_config(task: Task):
    task.run(
        name="Uplink interface to dhcp server",
        task=netmiko_send_command,
        command_string=f"disp mac-address vlan {task.host['vlan']} | inc {task.host['ser_mac']}",
    )

    task.run(
        task=write_file,
        filename=f"logs/{task.host.name}.txt",
        content=result_content(task),
        severity_level=logging.DEBUG,
    )

    parsed = parse_genie("huawei", "disp mac", task.results[0].result)
    task.host["parsed_intf"] = list(
        parsed["mac_table"]["vlans"][str(task.host["vlan"])]["mac_addresses"][task.host["ser_mac"]
        ]["interfaces"].items()
    )[0][0]

    return Result(host=task.host, result=task.host["parsed_intf"])


def send_config(task: Task, cli_tpl: str):
    task.run(
        name="Render config",
        task=template_file,
        template=cli_tpl,
        path="inventory/",
        severity_level=logging.DEBUG,
    )

    task.run(
        name="Send config",
        task=netmiko_send_config,
        config_commands=task.results[0].result.split("\n"),
    )

    task.run(
        task=write_file,
        filename=f"logs/{task.host.name}.txt",
        content=result_content(task),
        append=True,
        severity_level=logging.DEBUG,
    )


def verify_config(task: Task):
    task.run(
        name="DHCP snooping configuration",
        task=netmiko_send_command,
        command_string=f"display dhcp snooping configuration",
    )

    task.run(
        task=write_file,
        filename=f"logs/{task.host.name}.txt",
        content=result_content(task),
        append=True,
        severity_level=logging.DEBUG,
    )

    parsed = parse_genie("huawei", "disp dhcp", task.results[0].result)
    # Verify dhcp snooping enabled globally and vlan
    assert parsed["enabled"] == True, "DHCP snooping globally not enabled"
    assert (parsed["vlans"][str(task.host["vlan"])]["enabled"] == True
    ), f"DHCP snooping vlan {task.host['vlan']} not enabled"


if __name__ == "__main__":
    print_title("Nornir Playbook to configure DHCP Snooping")
    nr = InitNornir(config_file="config.yaml")

    print_title("Running on Test env")
    test_env = nr.filter(F(groups__contains="Test"))
    # Get trusted interface and backup state
    result = test_env.run(task=get_config)
    print_result(result)
    # Config
    result = test_env.run(task=send_config, cli_tpl="cli-dhcpsnoop-en.j2")
    print_result(result)

    # Verification
    result = test_env.run(task=verify_config)
    print_result(result)

    print_title("Running on Prod env")
    prod_env = nr.filter(F(groups__contains="Prod"))
    # Repeat