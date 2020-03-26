![Test CI](https://github.com/10sr/ansible-modules-pm2/workflows/Test%20CI/badge.svg)


ansible-modules-pm2
===================

Manage processes via [pm2](https://pm2.keymetrics.io/)

- Manage the state of processes via pm2 process manager
- Start/Stop/Restart/Reload/Delete applications



Usage
=====


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


License
=======

This software is licensed under GPLv3. See `LICENSE` for details.
