# Introduction to Ansible

So we used the vagrant shell provisioner earlier. Shell scripts are easy enough to use, ideal for simple use cases. But shell scripts become large and unwieldy when you use it for larger projects. So, we will look at a new tool called Ansible. 

Ansible is an open source configuration management tool.

It uses YAML to declaratively specify the desired state of an infrastructure.
This declarative specification can then be used to bring VMs from their current state to the desired state.

## Ansible concepts

Let me introduce you to some basic Ansible concepts.
Ansible is vast and feature rich, but let us first just about enough features to be able to use them.

## Target nodes
Target nodes are the VMs that you wish to configure using Ansible.

## Control nodes
A control node is where you run ansible from, in order to configure the target nodes.

## Modules
Ansible ships with a number of modules by default, that the users can use to configure VMs. 
You can browse through the module library [here](https://docs.ansible.com/ansible/latest/modules/modules_by_category.html).

In addition to the modules available out of the box, users can also write their own modules for reusable code.


## Tasks
Tasks are the building blocks of Ansible.
Ansible tasks provide an abstraction over system commands. 
Each task declaration that you make using ansible's YAML specification translates to a system command that ansible then executes on the target host, typically over SSH.

### Roles
A role is a group of tasks combined together to form a logical grouping.

Think of a VM that plays the role of a web server, or a database server.

In order to equip a VM to play the role of a web server, you would need a series of tasks, i.e. installing the web app, configuring the server software like apache or nginx, specifying the configuration files, starting the appropriate services etc. Each of these actions correspond to a specific task.

Similarly, to configure a VM to play the role of a database, you would need a series of tasks like mounting the disks, creating the directory structure, installing the database software, configuring the services, etc.

### Inventory
An inventory defines the servers that ansible would manage. 
There are various ways to specify an inventory, ranging from a simple static file to a program that will execute code to determine the list of VMs.


### Playbooks
Playbooks are the declarative files that associate hosts defined in the inventory to their roles.


## Installing Ansible.


### Prerequisites
Python is a prerequisite for ansible.
So download the latest python3 package from [the python website](https://www.python.org/downloads/) and install it, if you do not already have python3 in your machine.

It is desireable to install python modules inside specific `virtual environments`. 
So let us create a virtual environment for our use:

```
python3 -m virtualenv ~/.virtualenvs/ansible_tutorial
```

Once the virtual environment is created, activate it using the following command:

```
~/.virtualenvs/ansible_tutorial
```


### Installing ansible
Ansible is a python module, available as a pip package.
So all you need to install ansible is to run the command

```
pip install ansible
```

## A simple example using Ansible

Let us now use ansible to implement the static file serving example that we implemented in Chapter 4 using shell script.


Create the following Vagrantfile

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yaml"
  end
end
```

The vagrantfile is very similar to what we have seen earlier. 
Except, we have specified the provisioner to be Ansible.

We have also specified a playbook parameter. 
This refers to a playbook file.

Let us now write our ansible code

Run the following commands from the directory containing your Vagrantfile

```
mkdir server server/files server/tasks
touch playbook.yaml server/files/index.html server/tasks/main.yaml
```


The resultant file structure should look like this:

```
.
├── playbook.yaml
└── server
    ├── files
    │   └── index.html
    └── tasks
        └── main.yaml
```



Now modify the `playbook.yaml` file to contain the following content:

```
---

- name: Simple Playbook
  hosts: all
  roles:
    - server
  become: true
```

Here, the playbook tells ansible to apply the role named `server` on all the hosts.
Currently our Vagrantfile provisions only one VM, so running the role on `all` servers is okay.
We will look at how to work with inventories and target specific roles to specific VMs later on.

We also specify the `become: true` parameter. This ensures that all the commands, as determined by the tasks defined in the server role, are run with privilege escalation, i.e. the `sudo` prefix.

Let us now define the `server` role.

Modify the `servers/tasks/main.yaml` to contain the following content:

```
---

- name: Install nginx
  apt:
    name: nginx
    state: present
    update_cache: true

- name: Copy index file
  copy:
    src: index.html
    dest: /var/www/html/index.html

```


Here, we use the built in `apt` module to install nginx.
The `update_cache: true` parameter indicates that we need to run `apt-get update` before we attempt to install `nginx`.


Then we use the `copy` module to copy the html file.
Ansible looks for the source file in a directory called `files` within the role directory.
We haven't created the file yet, so let us create that.

Modify the `servers/files/index.html` to contain the following content, just like we did earlier.

```
<html>
    <head>
        <title>Hello from inside the vagrant VM</title>
    </head>
    <body>
        <h1>Hello World!</h1>
    </body>
</html>
```



Now, run `vagrant up`.

You can see that Ansible provisioner runs after VM creation.

As always, you can run `ansible provision` to run the provisioner again after having made any changes.

