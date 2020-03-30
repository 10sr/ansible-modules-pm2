#!/usr/bin/env python

import re
import sys

import jinja2
import yaml
from tabulate import tabulate

from ansible.modules.pm2 import pm2


def main(argv):
    doc_yaml = pm2.DOCUMENTATION
    examples_yaml = pm2.EXAMPLES
    returns_yaml = pm2.RETURN

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    tpl = env.get_template(argv[1])

    doc = yaml.safe_load(doc_yaml)

    arguments_header = ("Parameters", "Choices", "Comments")
    arguments_body = []
    for k, v in doc["options"].items():
        parameters = k
        if v.get("required", False):
            parameters = parameters + " (required)"

        choices = []
        for e in v.get("choices", []):
            if e == v.get("default"):
                choices.append(f"`{e}` (default)")
            else:
                choices.append(f"`{e}`")

        comments = []
        for e in v.get("description", []):
            e = re.sub(r"C\(([^)]+)\)", r"`\1`", e)
            e = re.sub(r"I\(([^)]+)\)", r"`\1`", e)
            comments.append(e)

        arguments_body.append((parameters, "<br>".join(choices), "<br>".join(comments)))

    print(
        tpl.render(
            arguments_table=tabulate(
                arguments_body, headers=arguments_header, tablefmt="github"
            ),
            examples=examples_yaml.strip(),
            descriptions=doc["description"],
        )
    )
    return


if __name__ == "__main__":
    main(sys.argv)
