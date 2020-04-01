[![Github Actions](https://github.com/10sr/ansible-modules-pm2/workflows/CI/CD/badge.svg?branch=master&event=push)](https://github.com/10sr/ansible-modules-pm2/actions)
[![PyPI](https://img.shields.io/pypi/v/ansible-modules-pm2)](https://pypi.org/project/ansible-modules-pm2/)



ansible-modules-pm2
===================

Ansible Module to Manage Processes via [PM2](https://pm2.keymetrics.io/)

- Manage the state of processes via pm2 process manager
- Start/Stop/Restart/Reload/Delete applications



Tested on:

- Host Python: 3.8
- Target host Python: 2.7, 3.5, 3.6, 3.7, 3.8
- Ansible: 2.8.10, 2.9.6 (Should work with older versions)


Installation
------------

Install via pip:

```shell
pip install ansible-modules-pm2
```


PM2 package have to be installed to target hosts.
For example, add following to your playbook to install pm2 globally:


```yaml
- npm:
    name: pm2
    global: yes
```



Usage
=====

Basic usage is similar to one of `service` or `supervisorctl` module:
specify the name and its state. To start an app `script` or `config`
have to be given.


Examples
--------


```yaml
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
```


Arguments
---------

| Parameters      | Choices                                                                                | Comments                                                                                                                                                                                                                                                                                                  |
|-----------------|----------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| name (required) |                                                                                        | Name of the application.<br>Required for all cases to check current status of app                                                                                                                                                                                                                         |
| state           | `started` (default)<br>`stopped`<br>`restarted`<br>`reloaded`<br>`absent`<br>`deleted` | `started`/`stopped`/`absent`/`deleted` are idempotent actions that will not run commands unless necessary.<br>`restarted` will always restart the process.<br>`reloaded` will always reload.<br>Note that `restarted` will fail when the process does not exist (action does not start it automatically). |
| config          |                                                                                        | Process configuration file, in JSON or YAML format.<br>Either `config` or `script` is required when `state=started`.                                                                                                                                                                                      |
| script          |                                                                                        | Executalbe file to start.<br>Either `config` or `script` is required when `state=started`.                                                                                                                                                                                                                |
| executable      |                                                                                        | Path to pm2 executable.                                                                                                                                                                                                                                                                                   |
| chdir           |                                                                                        | Change into this directory before running pm2 start command.<br>When `state=started` and this option is omitted, use the directory where `config` or `script` exists.                                                                                                                                     |

License
=======

This software is licensed under GPLv3. See `LICENSE` for details.
