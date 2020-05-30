
## Deploying a simple python web app using ansible

Let us now attempt something far more sophisticated than anything we have attempted so far.

Let us deploy a simple python web app to a VM.
Let us do this using production grade configuration.
And let us do that using Ansible.

Here is the world's simplest python web app. 

Create a file `app.py` with the following content.

```
def app(environ, start_response):
        data = b"Hello, World!\n"
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

This web app does not use any web framework. It however, uses the WSGI interface implementation that is used by all web frameworks. This means that the strategies used to deploy this web app, can also be used to deploy complex web applications written in python.

Run the command 

```
python app.py
```

Now browse to `http://localhost:8080`.

Confirm that it works.

So how do we deploy python web applications?

A typical configuration looks like this:

* We use a WSGI compatible HTTP Server like Gunicorn or uWSGI to serve the app at a port, say 5000.
* We use mechanisms like systemd or init.d or even a process control system like supervisord to make sure the Http Server keeps running at all times.
* Use Nginx as a reverse proxy to proxy, we tunnel traffic from 80 (HTTP) and 443 (HTTPS) to the port 5000, and also for other features like SSL termination.

Let us now implement this using ansible.

Let us start with a simple 1 node cluster. This would be our `cluster.json`
```
{
    "nodes": [
        {
            "host_name": "web-01",
            "port_mappings": [
                { "guest_port": 80, "host_port": 8080, "host_ip": "127.0.0.1" },
                { "guest_port": 5000, "host_port": 5000, "host_ip": "127.0.0.1" },
                { "guest_port": 22, "host_port": 22003, "host_ip": "127.0.0.1" }
            ],
            "network_configs": [
                { "ip": "192.167.32.3", "name": "vboxnet0", "adapter": 2 }
            ]
        }
    ]
}
```

Here is the `Vagrantfile`

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

nodes_config = (JSON.parse(File.read("cluster.json")))['nodes']

Vagrant.configure("2") do |config|

  nodes_config.each do |node|

    config.vm.define node["host_name"] do |vm_config|

      vm_config.vm.box = "hashicorp/bionic64"
      vm_config.vm.hostname = node["host_name"]

      vm_config.vm.provider "virtualbox" do |vb|
        vb.memory = 512
        vb.cpus = 1
      end

      port_mappings = node["port_mappings"]

      port_mappings.each do |port_mapping|
        vm_config.vm.network "forwarded_port", 
          guest: port_mapping["guest_port"], 
          host: port_mapping["host_port"], 
          host_ip: port_mapping["host_ip"]
      end

      network_configs = node["network_configs"]

      network_configs.each do |network_config|
        vm_config.vm.network "private_network", 
            ip: network_config['ip'], 
            name: network_config['name'], 
            adapter: network_config['adapter']
      end
    end
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yaml"
    ansible.inventory_path = "inventory.py"
  end
  
end

```


This would be `inventory.py` same as before.

```
#!/usr/bin/env python

import os
import sys
import argparse
import json

class ExampleInventory(object):

    _inventory = {
        'webservers': {
            'hosts': ['web-01'],
        },
        '_meta': {
            'hostvars': {
                'web-01': {
                    'ansible_host': '127.0.0.1',
                    'ansible_port': '22003',
                    'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key'
                }
            }
        }
    }

    _empty_inventory = {'_meta': {'hostvars': {}}}

    def __init__(self):
        
        self.read_cli_args()

        if self.args.list:  # Called with `--list`
            print(json.dumps(self._inventory))

        elif self.args.host:  # Called with `--host [hostname]`
            print(json.dumps(self.get_host_vars(self.args.host)))
        
        else: 
            print(json.dumps(self._empty_inventory))
        

    def get_host_vars(self, hostname):
        return self._inventory['_meta']['hostvars'][hostname]


    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()


# Get the inventory.
ExampleInventory()

```

Now let us create the directory structure

```
mkdir web web/tasks web/files web/files/code
touch playbook.yaml inventory.py web/tasks/main.yaml web/tasks/webapp.yaml 
touch web/files/code/app.py web/files/code/requirements.txt
```

Let us first place the code in the `app.py` file.
Modify the contents so that the file looks like this:

```
def app(environ, start_response):
        data = b"Hello, World!\n"
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

Modify the `requirements.txt` that it looks like this:

```
gunicorn
```

Modify the `playbook.yaml` so that it looks like this:

```
---

- name: Configure web servers
  hosts: webservers
  roles:
    - web
  become: true

```

### Copy the code into the VM

Define the web roles main task file `web/tasks/main.yaml`

```
---

- include: webapp.yaml
```

Here we are introduced to the concept of includes.
Includes let us split a large task file to multiple task files.

Let us define the included `webapp.yaml` task file.

```
- name: Install packages
  apt:
    name: ["python3", "python3-venv"]
    state: present


- name: Create the app path
  file:
    path: /opt/webapp
    state: directory
    owner: vagrant
    group: vagrant


- name: Create the virtual env
  shell: python3 -m venv /opt/webapp/venv
  args:
    creates: /opt/webapp/venv/bin/activate


- name: Create the requirements file
  copy:
    src: code/requirements.txt
    dest: /opt/webapp
    owner: vagrant
    group: vagrant
    mode: '0644'

- name: Create the code file
  copy:
    src: code/app.py
    dest: /opt/webapp
    owner: vagrant
    group: vagrant
    mode: '0644'


- name: Install python requirements in virtualenv
  shell: /opt/webapp/venv/bin/pip install -r /opt/webapp/requirements.txt
```

What did we do here?
First we installed the `python3` and `python-venv` packages.
Then we  created the directory that will contain the code.
We then created a virtual environment where we will install all our python dependencies.
Then we created the code and the requirements file.
Then we installed all the dependencies defined in the `requirements.txt` into the virtual env.

Run the `vagrant up` command to bring everything up.

Now SSH into the vm using the `vagrant ssh` command and confirm that everything is in place.

Run the following command

```
cd /opt/webapp/
python /opt/webapp/venv/bin/python app.py
```

Now browse the URL `http://localhost:5000` from the browser in your host to make sure that this works.
Remember, we mapped the `5000` port on the guest to the `5000` port in the host.

### Using Gunicorn
Gunicorn lets us run multiple worker processes for the web server. 

Let us see that in action.

SSH into the VM and the VM, run the command

```
sudo gunicorn -b 0.0.0.0:5000 -w 4 app:app
```
The `-w 4` command parameter specifies that Gunicorn needs to run 4 worker processes to handle requests.

Now browse to the port `5000` on the browser.

Press `Ctrl+C` to stop the command.

Let us now create a gunicorn parameters file in the VM.

Create a file `gunicorn.conf.py`

```
touch web/files/gunicorn.conf.py
```

Now copy the following contents into the file


```
import os
import multiprocessing


loglevel = 'info'
errorlog = '/var/log/gunicorn-error.log'
accesslog = '/var/log/gunicorn-access.log'

bind = '0.0.0.0:5000'
workers = multiprocessing.cpu_count() * 2 + 1

timeout = 3 * 60  # 3 minutes
keepalive = 24 * 60 * 60  # 1 day

capture_output = True
```


Now let us place a gunicorn configuration file in the VM using ansible.

Add the following task to `webapp.yaml`

```
- name: Create the gunicorn conf file
  copy:
    src: gunicorn.conf.py
    dest: /opt/webapp
    owner: vagrant
    group: vagrant
    mode: '0644'
```


### Running the gunicorn using supervisord

We will now use Supervisord to run the gunicorn command.
Supervisord provides process control features. It provides crash recovery and ensures that the web app is running at all times


Modify the `Install packages` task to include `supervisord`

```
- name: Install packages
  apt:
    name: ["python3", "python3-venv", "supervisor"]
    state: present

```

Now create the supervisor configuration file `app_supervisor.conf`

```
touch web/files/app_supervisor.conf
```

Now modify the contents of the file to be as follows:

```
[program:app]
user = root
directory= /opt/webapp
command=/opt/webapp/venv/bin/gunicorn -c gunicorn.conf.py app:app
autostart=true
autorestart=true
stderr_logfile = /var/log/supervisor_err.log
stdout_logfile = /var/log/supervisor_out.log
stopsignal=INT
```

Now let us place the configuration file and get the supervisord process to load it.
Modify the `webapp.yaml` to include the following tasks:

```

- name: Create the supervisord conf
  copy:
    src: app_supervisor.conf
    dest: /etc/supervisor/conf.d/
    owner: vagrant
    group: vagrant
    mode: '0644'


- name: Reload supervisord
  service:
    name: supervisor
    state: reloaded
    enabled: true
```

Now provision the VM again using the `vagrant provision` command.


### Installing and configuring nginx.

Now let us implement reverse proxy to forward the traffic from port 80 to the gunicorn managed web app running at port 5000.


Modify the `web/tasks/main.yaml` to include another task file that runs before the `webapp.yaml` tasks file.

```
---

- include: nginx.yaml
- include: webapp.yaml
```

Let us create the files required to deploy nginx.

```
touch web/tasks/nginx.yaml web/files/nginx.conf
```

Let us first create the nginx configuration file.
Modify the `nginx.conf` file to have the following content:

```
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
}

http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 2048;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;
    

    include /etc/nginx/sites-enabled/*.conf;
    server_names_hash_bucket_size 64;
}


```

Now, modify the `nginx.yaml` file to have the following content:

```
---

- name: Install nginx
  apt:
    name: nginx
    state: present
    update_cache: true

- name: Create the nginx config file
  copy:
    src: nginx.conf
    dest: /etc/nginx/
    owner: root
    group: root
    mode: '0644'


- name: create sites-available directory
  file:
    path: /etc/nginx/sites-available
    state: directory
    owner: root
    group: root


- name: create sites-enabled directory
  file:
    path: /etc/nginx/sites-enabled
    state: directory
    owner: root
    group: root


- name: Reload nginx
  service:
    name: nginx
    state: restarted
    enabled: true
```

In this task file, we installed nginx, copied over the nginx configuration file and created the appropriate directories as required by nginx, and then reloaded the nginx service to load the latest configuration file.


### Serving the app using nginx.

Create the nginx configuration file for serving the app

```
touch web/files/app-nginx.conf
```

Modify the contents to be as follows:

```
server {
    listen 80;

    location /content {
        root  /vagrant/content;
        try_files $uri $uri/ =404;
        autoindex on;
    }

    location / {
        proxy_pass         "http://localhost:5000";
        proxy_redirect     off;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        fastcgi_read_timeout 300s;
        proxy_read_timeout 300;
    }
}

```

This instructs the nginx server to forward traffic on port 80 to the web app running on port 5000


Now modify the `webapp.yaml` to deploy this configuration file.
Append the following to the `webapp.yaml`

```


- name: Create nginx server block for the nginx app
  copy:
    src: app-nginx.conf
    dest: /etc/nginx/sites-available
    owner: root
    group: root
    mode: '0644'


- name: Create symlink for the nginx app
  file:
    src: /etc/nginx/sites-available/app-nginx.conf
    dest: /etc/nginx/sites-enabled/app-nginx.conf
    state: link


- name: Reload nginx
  service:
    name: nginx
    state: restarted
    enabled: true


```


Now provision the VM using the `vagrant provision` command and browse to `http://localhost:8080` which will forward the traffic to the port 80 on the VM.

You can see that web app running.

