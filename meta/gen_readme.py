#!/usr/bin/env python

import sys

import yaml
import jinja2

from ansible.modules.pm2 import pm2


def main(argv):
    doc_yaml = pm2.DOCUMENTATION
    examples_yaml = pm2.EXAMPLES
    returns_yaml = pm2.RETURN

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    tpl = env.get_template(argv[1])

    doc = yaml.safe_load(doc_yaml)

    print(tpl.render(examples=examples_yaml.strip(), descriptions=doc["description"]))
    return


if __name__ == "__main__":
    main(sys.argv)
