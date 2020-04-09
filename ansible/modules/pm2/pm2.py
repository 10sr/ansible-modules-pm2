#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import os

from ansible.module_utils import pm2
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    "status": ["preview"],
    "supported_by": "community",
    "metadata_version": pm2.__version__,
}

DOCUMENTATION = """
---
module: pm2
author:
  - "10sr (@10sr)"
version_added: "-"
short_description: Manage processes via pm2
description:
  - Manage the state of processes via pm2 process manager.
  - Start/Stop/Restart/Reload/Delete applications.

options:
  name:
    required: true
    description:
      - Name of the application.
      - Required for all cases to check current status of app
  state:
    choices: [started, stopped, restarted, reloaded, absent, deleted]
    default: started
    description:
      - C(started)/C(stopped)/C(absent)/C(deleted) are idempotent actions
        that will not run commands unless necessary.
      - C(restarted) will always restart the process.
      - C(reloaded) will always reload.
      - Note that C(restarted) will fail when the process does not
        exist (action does not start it automatically).
  config:
    default: null
    description:
      - Process configuration file, in JSON or YAML format.
      - Either I(config) or I(script) is required when I(state=started).
  script:
    default: null
    description:
      - Executalbe file to start.
      - Either I(config) or I(script) is required when I(state=started).
  executable:
    default: null
    description:
      - Path to pm2 executable.
  chdir:
    default: null
    description:
      - Change into this directory before running pm2 start command.
      - When I(state=started) and this option is omitted, use the
        directory where I(config) or I(script) exists.
"""

EXAMPLES = """
---
- name: Start myapp with process config file, if not running
  pm2:
    name: myapp
    config: /path/to/myapp/myapp.json
    state: started

- name: Start myapp.js, if not running
  pm2:
    name: myapp
    script: /path/to/myapp/myapp.js
    state: started

- name: Stop process named myapp, if running
  pm2:
    name: myapp
    state: stopped

- name: Restart myapp, in all cases
  pm2:
    name: myapp
    state: restarted

- name: Reload myapp, in all cases
  pm2:
    name: myapp
    state: reloaded

- name: Delete myapp, if exists
  pm2:
    name: myapp
    state: absent

- name: Specify pm2 executable path
  pm2:
    name: myapp
    state: started
    config: /path/to/myapp/myapp.json
    executable: /path/to/myapp/node_modules/.bin/pm2

- name: Also specify working directory where running pm2 command
  pm2:
    name: myapp
    state: started
    config: /path/to/myapp/myapp.json
    executable: /path/to/myapp/node_modules/.bin/pm2
    chdir: /path/to/working/directory
"""

RETURN = """
---
pm2_state:
  description: Pm2 application status
  returned: success
  type: string
  sample: online
pm_id:
  description: Pm2 application id
  returned: success
  type: int
  sample: 3
pid:
  description: Application process id
  returned: success
  type: int
  sample: 514
"""


__metaclass__ = type


class _TaskFailedException(Exception):
    def __init__(self, msg, **kargs):
        self.msg = msg
        self.kargs = kargs
        return


class _Pm2App(object):
    """Class for one pm2 app."""

    # application info
    info_raw = None
    pm_id = -1
    pid = -1
    # None if app is not registered to pm2
    pm2_status = None

    def __init__(self, module, name, pm2_executable):
        self.module = module
        self.name = name
        if pm2_executable is None:
            self.pm2_executable = module.get_bin_path("pm2", required=True)
        else:
            self.pm2_executable = pm2_executable

        self._run_pm2(["--version"], check_rc=True)
        self._update_info()
        return

    def start_with_config(self, target, chdir=None):
        assert target is not None
        if chdir is None:
            target = os.path.abspath(target)
            chdir = os.path.dirname(target)
        rc, out, err = self._run_pm2(["start", target], check_rc=True, cwd=chdir)
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def start_script(self, target, chdir=None):
        assert target is not None
        if chdir is None:
            target = os.path.abspath(target)
            chdir = os.path.dirname(target)
        rc, out, err = self._run_pm2(
            ["start", target, "--name", self.name], check_rc=True, cwd=chdir
        )
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def stop(self):
        rc, out, err = self._run_pm2(["stop", self.name], check_rc=True)
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def delete(self):
        rc, out, err = self._run_pm2(["delete", self.name], check_rc=True)
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def restart(self):
        rc, out, err = self._run_pm2(["restart", self.name], check_rc=True)
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def reload(self):
        rc, out, err = self._run_pm2(
            ["reload", self.name, "--update-env"], check_rc=True
        )
        self._update_info()
        return {"rc": rc, "stdout": out, "stderr": err}

    def is_started(self):
        return self.pm2_status == "online"

    def exists(self):
        return self.pm2_status is not None

    def _run_pm2(self, args, check_rc=False, cwd=None):
        return self.module.run_command(
            args=([self.pm2_executable] + args), check_rc=check_rc, cwd=cwd
        )

    def _update_info(self):
        self.info_raw = None
        self.pm_id = -1
        self.pid = -1
        self.pm2_status = None

        rc, out, err = self._run_pm2(["jlist", "--silent"], check_rc=True)
        try:
            apps = self.module.from_json(out)
        except ValueError as e:
            raise _TaskFailedException(rc=1, msg=e.args[0])
        try:
            for app in apps:
                if app["name"] == self.name:
                    self.info_raw = app
                    break
        except KeyError:
            raise _TaskFailedException(
                msg="Unexpected pm2 jlist output format: {}".format(out)
            )

        if self.info_raw is None:
            # app is not registered
            return

        try:
            self.pm_id = self.info_raw["pm_id"]
            self.pid = self.info_raw["pid"]
            self.pm2_status = self.info_raw["pm2_env"]["status"]
        except KeyError:
            raise _TaskFailedException(
                msg="Unexpected pm2 jlist output: {}".format(self.info_raw)
            )
        return


def do_pm2(module, name, config, script, state, chdir, executable):
    result = {}
    pm2 = _Pm2App(module, name, executable)

    result["diff"] = {}
    result["diff"]["before"] = {
        "pm_id": pm2.pm_id,
        "pid": pm2.pid,
        "pm2_status": pm2.pm2_status,
    }

    if state == "started":
        if pm2.is_started():
            result.update(changed=False, msg="{} already started".format(name))
        else:
            if not module.check_mode:
                if config:
                    cmd_result = pm2.start_with_config(config, chdir=chdir)
                elif script:
                    cmd_result = pm2.start_script(script, chdir=chdir)
                else:
                    raise _TaskFailedException(
                        msg="Neigher CONFIG nor SCRIPT is given for start command"
                    )
                result.update(cmd_result)
            result.update(changed=True, msg="Started {}".format(name))

    elif state == "stopped":
        if not pm2.is_started():
            result.update(changed=False, msg="{} already stopped/absent".format(name))
        else:
            if not module.check_mode:
                cmd_result = pm2.stop()
                result.update(cmd_result)
            result.update(changed=True, msg="Stopped {}".format(name))

    elif state == "restarted":
        if config:
            module.warn("CONFIG is ignored when state is restarted")
        if script:
            module.warn("SCRIPT is ignored when state is restarted")
        if not module.check_mode:
            cmd_result = pm2.restart()
            result.update(cmd_result)
        result.update(changed=True, msg="Restarted {}".format(name))

    elif state == "reloaded":
        if config:
            module.warn("CONFIG is ignored when state is reloaded")
        if script:
            module.warn("SCRIPT is ignored when state is restarted")
        if not module.check_mode:
            cmd_result = pm2.reload()
            result.update(cmd_result)
        result.update(changed=True, msg="Reloaded {}".format(name))

    elif state == "absent" or state == "deleted":
        if not pm2.exists():
            result.update(changed=False, msg="{} not exists".format(name))
        else:
            if not module.check_mode:
                cmd_result = pm2.delete()
                result.update(cmd_result)
            result.update(changed=True, msg="Deleted {}".format(name))

    else:
        raise _TaskFailedException(msg="Unknown state: {]".format(state))

    result.update(pm_id=pm2.pm_id, pid=pm2.pid, pm2_status=pm2.pm2_status)
    result["diff"]["after"] = {
        "pm_id": pm2.pm_id,
        "pid": pm2.pid,
        "pm2_status": pm2.pm2_status,
    }

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            # TODO: Accept list of names for start_with_config
            name=dict(required=True),
            state=dict(
                choices=[
                    "started",
                    "stopped",
                    "restarted",
                    "reloaded",
                    "absent",
                    "deleted",
                ],
                default="started",
            ),
            config=dict(type="path"),
            script=dict(type="path"),
            executable=dict(type="path"),
            chdir=dict(type="path"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["config", "script"]],
    )

    try:
        result = do_pm2(
            module=module,
            name=module.params["name"],
            state=module.params["state"],
            config=module.params["config"],
            script=module.params["script"],
            executable=module.params["executable"],
            chdir=module.params["chdir"],
        )

    except _TaskFailedException as e:
        module.fail_json(failed=True, msg=e.msg, **e.kargs)
        return

    assert "changed" in result
    assert "msg" in result
    module.exit_json(failed=False, **result)
    return


if __name__ == "__main__":
    main()
