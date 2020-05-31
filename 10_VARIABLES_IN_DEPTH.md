# Ansible Variables in depth

## Defining variables at various scopes

Ansible is very flexible in terms of defining variables at various scopes. 
Namely, you can set variables at the following scopes

* CLI
* Inventory group and host
* Playbook
* Playbook group and host
* Role
* Task


In order to see these in action, let us first change the `custom_message.txt` file that gets rendered by our web app a little bit.


Change the `Create the custom message file` task to look like this:

```
- name: Create the custom message file
  template:
    src: custom_message.txt.j2
    dest: /opt/webapp/custom_message.txt
    owner: vagrant
    group: vagrant
    mode: '0644'
```

Let us also create the `custom_message.txt.j2` file that we referenced above:

```
touch web/templates/custom_message.txt.j2
```

### CLI variables

Modify the `custom_message.txt.j2` file to look like this:

```
{{ command_var1 }}
```

Now run the `ansible-playbook` command with the `--extra-vars` parameter as follows:

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`
You should see variable that we set from the CLI, reflected in the web pages.


### Inventory group and host variables

Modify the `_inventory` variable in your `inventory.py` file to specify two variables:

* The `inventory_group_var1` at the group level
* The `inventory_host_var1` at the host level


```
_inventory = {
    'webservers': {
        'hosts': ['web-01', 'web-02'],
        "vars": {
            'bind_address': 'localhost',
            'bind_port': '5000',
            'inventory_group_var1': "This is set as an inventory group variable from inventory.py line 16"

        }
    },
    '_meta': {
        'hostvars': {
            'web-01': {
                'ansible_ssh_host': '127.0.0.1',
                'ansible_port': '22003',
                'ansible_ssh_user': 'vagrant',
                'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key',
                'inventory_host_var1': "This is set as an inventory host variable from inventory.py line 27"
            },
            'web-02': {
                'ansible_ssh_host': '127.0.0.1',
                'ansible_port': '22004',
                'ansible_ssh_user': 'vagrant',
                'ansible_private_key_file': '.vagrant/machines/web-02/virtualbox/private_key',
                'inventory_host_var1': "This is set as an inventory host variable from inventory.py line 34"
            }
        }
    }
}
```

Now modify your `custom_message.txt.j2` to look like so:

```
{{ command_var1 }}
{{ inventory_group_var1 }}
{{ inventory_host_var1 }}
```

Now run the `ansible-playbook` command again.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`

You should see the two new variables also being rendered.
You can also see that the third line is now different for the two servers.


### Playbook variables

Now, modify your `playbook.yaml` to look like this:

```
---

- name: Configure web servers
  hosts: webservers
  roles:
    - web

  become: true
  vars:
    playbook_var1: "This is a variable set as a playbook variable from playbook.yaml line 10"
```

Now modify your `custom_message.txt.j2` to look like so:


```
{{ command_var1 }}
{{ inventory_group_var1 }}
{{ inventory_host_var1 }}
{{ playbook_var1 }}
```


Now run the `ansible-playbook` command again.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`

You should see the playbook variable being rendered too.


###  group and host variables at playbook level

Let us now set group and host variables at a playbook level

From the directory that contains the `playbook.yaml` file, run the following command

```
mkdir group_vars host_vars
touch group_vars/webservers.yaml
touch host_vars/web-01.yaml
touch host_vars/web-02.yaml
```

Now, modify the contents of the `group_vars/webservers.yaml` to be as follows:

```
---

playbook_group_var1: "This is a variable set as a playbook group variable from group_vars/webservers.yaml line 3"

```

Modify the contents of `host_vars/web-01.yaml` to be as follows:

```
---

playbook_host_var1: "This is a variable set as a playbook host variable from host_vars/web-01.yaml line 3"
```

Modify the contents of `host_vars/web-02.yaml` to be as follows:

```
---

playbook_host_var1: "This is a variable set as a playbook host variable from host_vars/web-02.yaml line 3"
```


Now modify your `custom_message.txt.j2` to look like so:

```
{{ command_var1 }}
{{ inventory_group_var1 }}
{{ inventory_host_var1 }}
{{ playbook_var1 }}
{{ playbook_group_var1 }}
{{ playbook_host_var1 }}
```


Now run the `ansible-playbook` command again.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`


You should see the two new variables also being rendered.
You can also see that the third line is now different for the two servers.

### Role variables

Let us now set role variables.

Run the following command from the directory that contains `playbook.yaml`

```
mkdir web/vars
touch web/vars/main.yaml
```

Now, modify the contents of `web/vars/main.yaml` to look like this:

```
---

role_var1: "This is a variable set as a role variable from web/vars/main.yaml line 3"
```

Now modify your `custom_message.txt.j2` to look like so:

```
{{ command_var1 }}
{{ inventory_group_var1 }}
{{ inventory_host_var1 }}
{{ playbook_var1 }}
{{ playbook_group_var1 }}
{{ playbook_host_var1 }}
{{ role_var1 }}
```

Now run the `ansible-playbook` command again.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`


You should see the role variable being rendered


### Task variables
Lastly, let us now set a task variable.

Modify your `Create the custom message file` task in the `webapp.yaml` task file to look like this.


```
- name: Create the custom message file
  template:
    src: custom_message.txt.j2
    dest: /opt/webapp/custom_message.txt
    owner: vagrant
    group: vagrant
    mode: '0644'
  vars:
    task_var1: "This variable is set as a task variable from web/tasks/webapp.yaml line 52"

```

Here, we added variables to the task.

Now modify your `custom_message.txt.j2` to look like so:


```
{{ command_var1 }}
{{ inventory_group_var1 }}
{{ inventory_host_var1 }}
{{ playbook_var1 }}
{{ playbook_group_var1 }}
{{ playbook_host_var1 }}
{{ role_var1 }}
{{ task_var1 }}
```

Now run the `ansible-playbook` command again.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --extra-vars "command_var1='Set from CLI'"
```

Now browse to `http://localhost:8080` and `http://localhost:8081`


You should see the task variable being rendered


## Variable precedence

As you can see, ansible lets you set variables at multiple levels. 
This makes the variable system very powerful.
It can also get very complicated, when you use same variable names at multiple levels. 

Generally you should avoid situations where you use clashing variable names at multiple levels. 
You can do this using a good naming convention.
Variables are not an inheritance mechanism.

But in case, you do end up using a clashing variable names by mistake, you will then have to understand the variable precedence. Refer the precedence resolution order from the official ansible documentation here:

https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable


Let me repeat, ending up in a situation where you use clashing variable names will most likely not end well for you. The fact that variables can be pulled programmatically from inventories and set dynamically at the CLI, combined with the fact that YAML is NOT a programming language which you can debug, will result in a lot of frustration.  Try to avoid that at all costs.


## Registering variables and Conditionals

Let us now make our ansible playbook runs a little more efficient.

So far, when we run our playbook, all tasks run, every single time. This can be inefficient.

For example, we restart the nginx service using this snippet in our `web\tasks\nginx.yaml`

```
- name: Reload nginx
  service:
    name: nginx
    state: restarted
    enabled: true
```

You can see from the output that nginx service gets restarted every single time.
This is not only unneccessary, put in some cases at scale, it can be downright unacceptable.
For example, restarting means a short downtime which we would want to avoid unless absolutely necessary.

So, how do you conditionally restart nginx? Ideally, we would like to restart nginx only if we have made major changes to the nginx configuration file. 

So how how do we detect if the nginx configuration file has changed? 
And how do we conditionally run the restart command?

To capture some state, we can use the ansible concept of register variables.
Let us see that in action.

Modify the `Create the nginx config file` task by adding a register keyword.
The task should now look like this:

```
- name: Create the nginx config file
  copy:
    src: nginx.conf
    dest: /etc/nginx/
    owner: root
    group: root
    mode: '0644'
  register: nginx_config
```

This registers a variable called `nginx_config`.

Let us now use this variable in the reload nginx task using the `when` keyword.


```
- name: Reload nginx
  service:
    name: nginx
    state: restarted
    enabled: true
  when: nginx_config.changed
```

Now, when have ensured that the restart command runs only if the configuration file has changed.

When we bring up the VM and run the playbook for the first time, you would notice this in your output

```
TASK [web : Reload nginx]
 *************************************************************
changed: [web-02]
changed: [web-01]
```


But for any subsequent playbook runs, you should see that the `Reload nginx` task is skipped.

```
TASK [web : Reload nginx] 
**************************************************************
skipping: [web-01]
skipping: [web-02]
```

We can similarly optimize the `Reload supervisord` and `Reload nginx` tasks in the `web\tasks\webapp.yaml` by conditionally running them.

i.e. Supervisord needs to be reloaded only if the following files have changed:
* The python code file `/opt/webapp/app.py`
* The gunicorn configuration file `/opt/webapp/gunicorn.conf.py`
* The supervisord configuration file `/etc/supervisor/conf.d/app_supervisor.conf`


```
....
....

- name: Create the code file
  copy:
    src: code/app.py
    dest: /opt/webapp
    owner: vagrant
    group: vagrant
    mode: '0644'
  register: code_file

....
....

- name: Create the gunicorn conf file
  template:
    src: gunicorn.conf.j2
    dest: /opt/webapp/gunicorn.conf.py
    owner: vagrant
    group: vagrant
    mode: '0644'
  register: gunicorn_conf


- name: Create the supervisord conf
  copy:
    src: app_supervisor.conf
    dest: /etc/supervisor/conf.d/
    owner: vagrant
    group: vagrant
    mode: '0644'
  register: supervisor_conf


- name: Reload supervisord
  service:
    name: supervisor
    state: reloaded
    enabled: true
  when: code_file.changed or gunicorn_conf.changed or supervisor_conf.changed
```



Similarly, the nginx service needs to be reloaded or restarted only if `/etc/nginx/sites-available/app-nginx.conf` has changed.

```
....
....


- name: Create nginx server block for the nginx app
  template:
    src: app-nginx.conf.j2
    dest: /etc/nginx/sites-available/app-nginx.conf
    owner: root
    group: root
    mode: '0644'
  register: nginx_app_conf

....
....

- name: Reload nginx
  service:
    name: nginx
    state: restarted
    enabled: true
  when: nginx_app_conf.changed
```

Destroy and recreate the VMs and then run the playbook command multiple times to see this in action.


## Loops

