# Handing secrets using Ansible Vault


## Creating secrets using Ansible vault

Ansible Vault is an ansible feature that lets you encrypt strings and files.
You can use ansible vault to use encrypted strings in your playbook, instead of storing secrets in plaintext.

Let us see the ansible vault feature in action.

Run the following command

```
ansible-vault create /tmp/foo.txt
```

This will prompt you for a vault password. Enter, and reconfirm the password.
Ansible vault will  create a file at `/tmp/foo.txt` and will use your password to encrypt it.

The command should open a text editor window, typically `vi`.

Edit the contents of the file and now save it.


Now view the contents of the file using the command

```
cat /tmp/foo.txt
```

You can see that the contents are in encrypted format.


To view the file in its unencrypted form, run 

```
ansible-vault edit /tmp/foo.txt
```

This should again prompt a password. Enter the password. This will open the editor again, and you will be able to view and edit the file in its unencrypted format.

if you do not like to be prompted every time with the vault password, you can store the password in a file.

```
echo helloworld > .vault_pass
```

then you can set the path the password file in an environment variable.

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-vault edit /tmp/foo.txt
```

Make sure to NOT add your password file to source control.


Ansible vault also lets you encrypt plain text strings. 
Run the following command

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-vault encrypt_string foobared
```

To make it easy to use in YAML files, you can also pass in key names, like so:


```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-vault encrypt_string foobared --name redis_password
```


## Using Ansible vault secrets in the playbook

In the last code example, we hardcoded the redis password in our playbook code. 
We hardcoded it in two places: in the `app.py` config file as well as in the `Set redis password` task in our `db` role.

Let us now modify our code to use ansible vault.

First up, let us modify the `app.py` file to read the redis host details from a configuration file. Modify it to look like so:

```
import socket
import redis
import json

def app(environ, start_response):

        with open('config.json') as config_file:
            config = json.load(config_file)
            redis_host = config["redis_host"]
            redis_password = config["redis_password"]

        r = redis.Redis(host=redis_host, password=redis_password)
        
        if r.exists("hit_count"):
            hit_count = int(r.get("hit_count"))
        else:
            hit_count = 1
        
        hit_count = hit_count + 1
        r.set("hit_count", hit_count)


        data = bytes("Hello World, this website has been visited {0} times".format(hit_count), 'utf-8')

        start_response("200 OK", [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(data)))
        ])
        return iter([data])


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, app)
    srv.serve_forever()

```

The code now reads the connection details from a json file called `config.json`.
Let us now modify our playbook code to create this file.

Add this task in your `webapp.yaml` right next to the `Create the code file` task


```
- name: Create the app config file
  template:
    src: app_config.json.j2
    dest: /opt/webapp/config.json
    owner: vagrant
    group: vagrant
    mode: '0644'
```

This task will look for a template called `app_config.json.j2` and create the file `config.json` in the same directory as `app.py`


Now, let us create the template file

```
touch web/templates/app_config.json.j2
```

Now, modify the contents of the file to look like this

```
{
    "redis_host": "{{ redis_host }}",
    "redis_password": "{{ redis_password }}"
}
```
We specify two variables in the template, `redis_host` and `redis_password`


Similarly, let us modify the db role task to use these variables instead.

Modify the `Allow redis to listen to IP on eth1` and `Set redis password` to use the `redis_password` variable.

```

- name: Allow redis to listen to IP on eth1
  lineinfile:
    dest: /etc/redis/redis.conf
    line: 'bind {{ redis_host }}'
    create: true

- name: Set redis password
  lineinfile:
    dest: /etc/redis/redis.conf
    line: 'requirepass {{ redis_password }}'
    create: true
```


So the variables are being used by both the `db` and `web` roles. Let us now create these variables.

```
mkdir groupvars/all
touch groupvars/all/vars.yaml
touch groupvars/all/vault.yaml
```

We are specifying group variables under the `all` group, which is a default catch all group which is a superset of all the specified groups.

Note that we are creating two files in the group vars. You will shortly see why we did that:

Modify the contents of the `groupvars/all/vars.yaml` to look like this

```
---
redis_host: "192.167.32.5"
redis_password: "{{ vault_redis_password }}"
```

Now, run the command to generate an encrypted string for the plain text password `foobared`

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-vault encrypt_string foobared --name vault_redis_password
```

It should show an output, like this

```
vault_redis_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    35646465623062653935343733616135376166613435316266616566363164343035343633346663
    3436636433336237653230366463303236353261386338640a353964643230316161396137353562
    66656532373161623763363334396435373162313430643663306531383334313262326237353737
    3435356238356432630a303836646138363633306463303432366564343162376361643838356364
    3938
Encryption successful
```

Now, copy the key value pair from the output in order to use in our `groupvars/all/vault.yaml` to look like this


```
---

vault_redis_password: !vault |
    $ANSIBLE_VAULT;1.1;AES256
    66393134343339653539393531346339376534653838663762653334383733356636643363313366
    3663363438643861373935306264323563386261306266390a613538366337646562346231346364
    37333337316230636466323035316330626236303462653338663661383435316633653561313561
    3833636263323935660a306566623234323264663836306664653937303536333931666666353335
    3661
```

So what did we do? 
In the value of the `redis_password` variable declared in `groupvars/all/vars.yaml`, we referenced another variable `vault_redis_password`.

We then defined the `vault_redis_password` variable in the `groupvars/all/vault.yaml`

This provides a nice separation of concerns where we can separate variable files that have encrypted content from the variable files that have plaintext configuration values.

This is considered a best practice in ansible.

To confirm if the variables are getting reflected properly, run the following command

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible -m debug -a 'var=hostvars[inventory_hostname]["redis_password"]' web-01 -i inventory.py
```

and 

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible -m debug -a 'var=hostvars[inventory_hostname]["redis_password"]' db-01 -i inventory.py
```

Here, we use the `ansible` cli to run an ad-hoc `debug` command that prints the value of the variables.

You should see output like this


```
web-01 | SUCCESS => {
    "hostvars[inventory_hostname][\"redis_password\"]": "foobared"
}
```

```
db-01 | SUCCESS => {
    "hostvars[inventory_hostname][\"redis_password\"]": "foobared"
}
```

Let us now deploy this code. Destroy and recreate your VMs and run the playbook with the following command

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml
```

## Using secret scripts

Similar to inventories, you can also use executable scripts to specify vault passwords.
Let us see that in action.

Create this file `vault_pass.py` in the directory that contains the `playbook.yaml`

```
touch vault_pass.py
chmod +x vault_pass.py
```

Now, modify the `vault_pass.py` file to print your password.

```
#!/usr/bin/env python
print("helloworld")
```

Verify that it works

```
./vault_pass.py
```

Now, let us use this file instead

```
ANSIBLE_VAULT_PASSWORD_FILE=vault_pass.py ansible -m debug -a 'var=hostvars[inventory_hostname]["redis_password"]' web-01 -i inventory.py
```

As you can see, the executable vault password works just as fine.
This feature is very useful when working in dynamic environments.