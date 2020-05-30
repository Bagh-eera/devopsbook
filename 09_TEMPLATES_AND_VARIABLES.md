# Templates, Variables and Secrets

## using templates and variables



In the previous chapter, we hardcoded a bunch of configurations in the files that get deployed into the VM.

For example, the port 5000 is hard coded in both the `gunicorn.conf.py` and the `app-nginx.conf` files.

In advanced cases, we would want to specify that port as a part of a configuration variable, and have that variable value specified in the file.

Enter templates. Ansible supports templating using the Jinja2 templating engine. Jinja2 is a robust, versatile templating engine popular among python developers.

Templating allows us to specify templates instead of files and substitute variables in the template files when they get provisioned.

Variables can be declared in your inventory.

Modify your `inventory.py` file to add the templating variables.

```
_inventory = {
        'webservers': {
            'hosts': ['web-01'],
        },
        '_meta': {
            'hostvars': {
                'web-01': {
                    'ansible_host': '127.0.0.1',
                    'ansible_port': '22003',
                    'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key',
                    'bind_address': 'localhost',
                    'bind_port': '5000'
                }
            }
        }
    }
```

Here, we declared two templating variables, `bind_address` and `bind_port`.

Now, let us use Ansible's templating mechanism to create files.

Create the `templates` directory and move over the `gunicorn.conf.py` and the `app-nginx.conf` files over.

```
mkdir web/templates
mv web/files/gunicorn.conf.py web/templates/gunicorn.conf.j2
mv web/files/app-nginx.conf web/templates/app-nginx.conf.j2
```

Here we are using the `j2` extension, which is typically used to denote Jinja2 templates.

Let us now use template variables in these template files.

In the `gunicorn.conf.j2` file, replace the line that specifies the bind address with the following line:

```
bind = '{{ bind_address}}:{{ bind_port }}'
```

Then, in the `app-nginx.conf`, replace the line where we specify the `proxy_pass` setting as follows:

```
proxy_pass         "http://{{ bind_address }}:{{ bind_port }}";
```

Now, modify your `webapp.yaml` task file to use these templates instead of files in the respective tasks

```
- name: Create the gunicorn conf file
  template:
    src: gunicorn.conf.j2
    dest: /opt/webapp/gunicorn.conf.py
    owner: vagrant
    group: vagrant
    mode: '0644'
```

and 

```
- name: Create nginx server block for the nginx app
  template:
    src: app-nginx.conf.j2
    dest: /etc/nginx/sites-available/app-nginx.conf
    owner: root
    group: root
    mode: '0644'
```

Bring up the VMs now. Once they are up, you can inspect the contents of the respective files to see that the variables have been substituted accordingly. SSH into the VM using `vagrant ssh` command and run the following commands

```
sudo cat /opt/webapp/gunicorn.conf.py
sudo cat /etc/nginx/sites-available/app-nginx.conf
```

We can even use the ansible variables in our tasks. Add this task anywhere in the `webapp.yaml` file, or any other task file for that matter.

```
- name : Print a debug message
  debug:
    msg: We are going to bind the web app at '{{ bind_address }}' address to listen on '{{ bind_port }}' port

```


You should see the following output

```
TASK [web : Print a debug message] *********************************************
ok: [web-01] => {
    "msg": "We are going to bind the web app at 'localhost' address to listen on '5000' port"
}
```

## System variables
Not all variables have to be explicitly declared.
Some variables are implicitly set by Ansible,s to be discoved and used by the system.

These variables are also called `facts`.

Put this debug statement at the top of the `nginx.yaml` file to see them

```
- name: Print system variables
  debug: 
    var: ansible_facts
```

You should see a large dictionary getting printed. It would look something like this:

```
ok: [web-01] => {
    "ansible_facts": {
        "all_ipv4_addresses": [
            "192.167.32.3",
            "10.0.2.15"
        ],
        "all_ipv6_addresses": [
            "fe80::a00:27ff:fe95:36c6",
            "fe80::a00:27ff:febb:1475"
...
...
...
```
Scroll through the printed facts. The dictionary has some interesting variables, and depending on certain usecases, there are some really creative ways to use them.

Replace the line that specifies the number of workers in the `gunicorn.conf.j2` file with this:

```
workers = {{ ansible_facts['processor_vcpus'] * 2 + 1 }}
```

Here, we read the number of processor vCPU available from the ansible facts, and use the arithmetic operations inside the Jinja2 templating to specify the number of workers.

Run the `vagrant provision` command and inspect the contents of the files using the following command:

```
sudo cat /opt/webapp/gunicorn.conf.py
```

You should see the number of workers set to 3. Because as per our `Vagrantfile`, each machine has 1 vCPU.
Thus `1*2+1` = `3`.


## Ansible CLI 

### The ansible command
Now that we are fairly comfortable with Ansible, this would be a good time to introduce the ANsible CLI commands. 


Add this one line `'ansible_user': 'vagrant',` to your `inventory.py` to specify a new variable called `ansible_user`. 

Your `_inventory` variable in the `inventory.py` file should now look like this:

```
_inventory = {
        'webservers': {
            'hosts': ['web-01'],
        },
        '_meta': {
            'hostvars': {
                'web-01': {
                    'ansible_host': '127.0.0.1',
                    'ansible_port': '22003',
                    'ansible_user': 'vagrant',
                    'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key',
                    'bind_address': 'localhost',
                    'bind_port': '5000'
                }
            }
        }
    }
```

Now, remove these lines from your `Vagrantfile`.

```
config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yaml"
    ansible.inventory_path = "inventory.py"
  end
```

We basically do not specify ANY provisioner in the Vagrantfile.
Vagrant is now only responsible for bringing up the VMs, not provisioning them.


Now, bring up the VM using `vagrant up`
Now, run this command:

```
ANSIBLE_HOST_KEY_CHECKING=False ansible all -i inventory.py -m ping
```

You should see the following output:

```
web-01 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
```

What just happened?


* We set the variable `ANSIBLE_HOST_KEY_CHECKING` to False, to prevent the command from blocking due to SSH key host checking. By default, the SSH client verifies the identity of the host to which it connects. When you log into a remote host that you have never connected before, the remote host key is most likely unknown to your SSH client, and you would be asked to confirm its fingerprint. And when we destroy that VM and spin up a new VM in its place, our local ssh agent throws a warning when we connect to a different VM. We disable this behaviour by disabling the host key checking. It is usually not reccomended to do that for production environments because this is a security mechanism, but in our case, we are spinning up VMs locally, so it is fine.


* We invoked the Ansible CLI using the `ansible` command.

* we specified a pattern `all` which means we are to run the command on all the VMs in our inventory.

* We passed the inventory file `inventory.py` using the `-i` command. This would tell the CLI the list of VMs to connect to.

* We ran the Ansible `ping` [module](https://docs.ansible.com/ansible/latest/modules/ping_module.html) directly from the CLI using the `-m` flag. 


This is called an `ad-hoc` command where we invoke the modules directly instead of specifying tasks or playbooks.

Here is another example of an `ad-hoc` command.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible web-01 -i inventory.py -m shell -a 'echo Hello world'
```

You should see an output like this:

```
web-01 | CHANGED | rc=0 >>
Hello world
```

Here, we ran the `echo Hello world` command on the `web-01` VM using the `shell` [module](https://docs.ansible.com/ansible/latest/modules/shell_module.html).


Both of these commands are fairly useless. So let us run something a bit more useful

```
ANSIBLE_HOST_KEY_CHECKING=False ansible web-01 -i inventory.py -m file -a 'path=/home/vagrant/hello.txt state=touch'
```
You should see this output:

```
web-01 | CHANGED => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": true,
    "dest": "/home/vagrant/hello.txt",
    "gid": 1000,
    "group": "vagrant",
    "mode": "0664",
    "owner": "vagrant",
    "size": 0,
    "state": "file",
    "uid": 1000
}
```

Here the CLI was a bit more useful. We created a file inside the VM using the CLI.

SSH into the VM using the `vagrant ssh` command and see for yourself using the `ls` command. You should see the `hello.txt` file in your home directory.

Ad-hoc commands are powerful. They let you run a command on multiple VMs at the same time.

They are also not reccomended. Because running ad-hoc commands will also introduce configuration drift. And that is against the DevOps principles. So use caution when you use them.


### The ansible-playbook CLI
Let us now use another CLI, `ansible-playbook`.

This lets us run ansible playbooks from the command line.

```
ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i inventory.py playbook.yaml
```

You can see the playbook running against the VM that we brought up. Just like usual.

So from now on, let us now run the `ansible-playbook` Ansible CLI commands directly.

From now on, Let us now not use the `Vagrantfile` to provision the VMs.




## Group variables
What if we want to share variables across multiple machines of similar types? 
Suppose we have 100 web frontend VMs.
Specifying the same variables for each of the 100 web frontend VMs can be cumbersome.
Enter group variables. 
Group variables are a convenient way to apply variables to multiple VMs at once.

Group variables are better illustrated if we have multiple VMs.

Add one more node to your `cluster.json` file.

```
{
  "host_name": "web-02",
  "port_mappings": [
      {
          "guest_port": 80,
          "host_port": 8081,
          "host_ip": "127.0.0.1"
      },
      {
          "guest_port": 5000,
          "host_port": 5001,
          "host_ip": "127.0.0.1"
      },
      {
          "guest_port": 22,
          "host_port": 22004,
          "host_ip": "127.0.0.1"
      }
  ],
  "network_configs": [
      {
          "ip": "192.167.32.4",
          "name": "vboxnet0",
          "adapter": 2
      }
  ]
}
```


Now, we want both of these VMs to serve the response on port 5000.
So, let us move the variable that declares the bind address and bind port from the individual node, to the group.

Modify the `_inventory` variable in your `inventory.py` so that it looks like this:

```
_inventory = {
    'webservers': {
        'hosts': ['web-01', 'web-02'],
        "vars": {
            'bind_address': 'localhost',
            'bind_port': '5000'
        }
    },
    '_meta': {
        'hostvars': {
            'web-01': {
                'ansible_ssh_host': '127.0.0.1',
                'ansible_port': '22003',
                'ansible_ssh_user': 'vagrant',
                'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key',
                'custom_message': 'Hello from VM 1'
            },
            'web-02': {
                'ansible_ssh_host': '127.0.0.1',
                'ansible_port': '22004',
                'ansible_ssh_user': 'vagrant',
                'ansible_private_key_file': '.vagrant/machines/web-02/virtualbox/private_key',
                'custom_message': 'Hello from VM 2'
            }
        }
    }
}
```

Things to note:
* We now have 2 VMs in the inventory.

* And the common variables `bind_address` and `bind_port` have been moved to the group.

* We also added a host specific variable called `custom_message`.


Now, add this task in your `webapp.yaml` file, right after the `Create the code file` task.

This task  will create a text file which has the content specified in the `custom_message` host variable.

```
- name: Create the custom message file
  copy:
    dest: /opt/webapp/custom_message.txt
    content: "{{ custom_message }}"
```


Let us now modify our python code to distinguish between VMs that are serving them. 

Modify your python code to read the file to read the text file that we just created. 

It should look like this:

```
import socket

def app(environ, start_response):

        with open('custom_message.txt') as file:
            contents = "".join(file.readlines())

        data = bytes(contents, 'utf-8')

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


Bring up your VMs using `vagrant up` command.

Now browse to `http://localhost:8080` and `http://localhost:8081`

You should see two different responses. Yay!

