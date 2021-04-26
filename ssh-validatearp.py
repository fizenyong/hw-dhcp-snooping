from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_title, print_result
from nornir_utils.plugins.tasks.files import write_file
from nornir.core.filter import F
from pyats import aetest
from genie_hw.parse import parse_genie
import dpath.util
import re
import logging
import json


def result_content(task: Task) -> str:
    content = []

    # Add display command (task name) of Result
    for r in task.results:
        if r.severity_level < 20:  # Skip if logging.DEBUG
            continue
        content.append(f"<{r.name}>")
        content.append(r.result)
        content.append("</end>\n")
    return "\n".join(content)


def get_aetest_result(aeresult_data: list) -> str:
    content = []

    # Format AEtest section result
    for r in aeresult_data:
        content.append(f"{r['name']:70.66}{r['result'].value.upper()}")
    return "\n".join(content)


def read_content(task: Task, fpath: str, pattern: str) -> Result:
    with open(fpath) as f:
        string = f.read()

    m = re.match(pattern, string)

    return Result(host=task.host, result=m[0])


def parse_cli(task: Task, command: str, cli: str) -> Result:
    # TODO: Use abstarction to load module
    # Rewrite parse_genie function to return result
    return Result(host=task.host, result=parse_genie("huawei", command, cli))


def run_aetest(task: Task, parsed_cli: dict, dictpath: str, testable: str) -> Result:
    # TODO: pass **kwargs to aetest
    aetest_result = aetest.main(
        testable=testable,
        generator=dpath.util.search(parsed_cli, dictpath, yielded=True),
    )

    result = get_aetest_result(aetest_result.data) + "\n" + str(aetest_result.code)

    return Result(host=task.host, result=result)


def verify_arp(task: Task):
    task.run(
        task=read_content,
        fpath=f"logs/{task.host.hostname}-{task.host.name}.txt",
        pattern=r"<disp arp all \| inc Eth-Trunk>\s(?P<content>[\s\S]+?)(?=<\/end>)",
    )

    task.run(
        task=parse_cli,
        command="disp arp",
        cli=task.results[0].result,
        severity_level=logging.DEBUG,  # Dict of parsed cli data
    )

    task.run(
        task=run_aetest,
        parsed_cli=task.results[1].result,
        dictpath="interfaces/Eth-Trunk3.*",
        testable="aetest/ae-validate-arp.py",
    )

    task.run(
        task=write_file,
        filename=f"logs/{task.host.name}.json",
        content=json.dumps(task.results[1].result, indent=4),
        severity_level=logging.DEBUG,
    )

    assert task.results[2].result[-1] == "1"


if __name__ == "__main__":
    print_title("Nornir Playbook to validate arp state")
    nr = InitNornir(config_file="config.yaml")

    print_title("Running on Test env")
    test_env = nr.filter(F(groups__contains="Test"))
    #test_env = nr.filter(F(hostname__contains="10.255.0.5"))

    # Verification
    result = test_env.run(task=verify_arp)
    print_result(result)

    print_title("Running on Prod env")
    prod_env = nr.filter(F(groups__contains="Prod"))
    # Repeat