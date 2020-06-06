# Tags, Handlers and blocks

## Tags
So we have written a lot of ansible code so far.
You can see that the codebase is becoming pretty big. 
Also, you notice that not all steps are required to be run every time we make a change.

For example, suppose we were to rotate the passwords of our redis server. 
Password rotations are a healthy practice. 
In this case, We would want to run only certain parts of the playbook in order to save us time.

Namely, we would want to run the `Create the app config file` task from our `web` role and the `Set redis password` task from our db role.

The tags feature in ansible lets us do exactly that.

We can specify tags on certain tasks, and then specify those tags in our `ansible-playbook` CLI invocation. The CLI will only run those certain files.

Let us see this in action.

Modify the `web\tasks\webapp.yaml` to look like so:

```
- name: Create the app config file
  template:
    src: app_config.json.j2
    dest: /opt/webapp/config.json
    owner: vagrant
    group: vagrant
    mode: '0644'
  tags: [rotate-db-password]
```

Here, the code mostly remains the same, we just added the extra `tags` property, which specifies an array that contains one tag, namely `rotate-db-password`.


Now, Modify the `db\tasks\main.yaml` to look like so:

```
- name: Set redis password
  lineinfile:
    dest: /etc/redis/redis.conf
    regexp: "^requirepass [a-zA-Z0-9]+$"
    line: 'requirepass {{ redis_password }}'
    create: true
  tags: [rotate-db-password]
```

Here we changed the `Set redis password` slightly. 
We specified the same tag `rotate-db-password` but we also added an additional parameter to the lineinfile module invocation, `regexp: "^requirepass [a-zA-Z0-9]+$"`. The `regexp` property allows us to replace the existing password that we already set. Without this line, the task would have simply created an additional `requirepass` declarative in the redis configuration file.

Now, let us run the playbook with the tags passed as parameters.

Run the following command:

```
ANSIBLE_VAULT_PASSWORD_FILE=vault_pass.py ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --tags="rotate-db-password"
```

You can see that the playbook ran much faster, because we only ran the two tagged tasks.


## Handlers

We wrote the code to change the password in the configuration files but the password change will not take affect until we restart the redis service. 

One way to achieve this is to add the tag to the `Restart redis service` task. 

But ansible provides a more elegant way. 

The Handlers feature in ansible lets us listen to certain events and trigger actions in response to those events.

Let us see that in action.

Modify the `Set redis password` task in the `db\tasks\main.yaml` file to look like this.


```
- name: Set redis password
  lineinfile:
    dest: /etc/redis/redis.conf
    regexp: "^requirepass [a-zA-Z0-9]+$"
    line: 'requirepass {{ redis_password }}'
    create: true
  tags: [rotate-db-password]
  notify:
  - restart redis
```

Here we specified a `notify` keyword. The `notify` keyword creates an event named `restart redis` that can then be listened to by handlers.

Let us now create the handler that will actually restart the service.

Run the following commands

```
mkdir db\handlers
touch db\handlers\main.yaml
```

Now modify the contents of `db\handlers\main.yaml` to look like this:

```
---

- name: restart redis
  service:
    name: redis
    state: restarted
```

The `restart redis` handler listens to the `restart redis` event and restarts the `redis` service when the event is triggered.

Let us see that in action. Invoke the `ansible-playbook` CLI again.


```
ANSIBLE_VAULT_PASSWORD_FILE=vault_pass.py ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --tags="rotate-db-password"
```

Observe the output carefully. Notice something odd? 

The handlers didn't actually get invoked. Why is that?

This is because, the `Set redis password` task ran without making any change to the system. The password was already set, because of that, the playbook ran that task without affecting any change. Because no change was affected, the handler saw no reason to run. This is a very clever design choice by Ansible. To see the handler getting invoked, you actually need to change the password.

Let usrun the command to generate an new encrypted string for the plain text password `fizzbuzz`

```
ANSIBLE_VAULT_PASSWORD_FILE=.vault_pass ansible-vault encrypt_string fizzbuzz --name vault_redis_password
```

Now, copy the key value pair from the output and replace the existing content in `groupvars/all/vault.yaml`

Now, run the playbooks again

```
ANSIBLE_VAULT_PASSWORD_FILE=vault_pass.py ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml --tags="rotate-db-password"
```

This time, you can see that the handlers are getting invoked.

Now browse to `http://localhost:8080` and `http://localhost:8081` and confirm that everything works fine.


