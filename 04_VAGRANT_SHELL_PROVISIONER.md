# Using the Shell provisoner

So in the last chapter, we created a VM.

That was fun. 

We immediately destroyed it though. We didnt do anything useful with it. 

Lets change that.

Let us get the VM to serve a static web page.

In the process we will learn how the shell provisoner works.


## The shell provisioner
The shell provisioner lets us execute a shell script inside the VM.
It is one of the easier provisoners to work with, and ideal for someone who is just getting started and not familiar with more sophisticated configuration management tools.

## Getting the VM to serve a static web page

### Installing Nginx inside the VM
Create a vagrant file using the `init` command and modify it so that looks like so:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"


  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y nginx
  SHELL
end

```

Here the Vagrantfile specifies a provisioner, and specifies the commands that it needs to run.
Basically, the provisioner tries to install nginx on the VM that brings up.

Now bring up the VM using the `up` command. 

Notice anything different when you run the command? You can see that the VM is executing the commands that we specified in the provisioner script.

Let us now verify that the provisioner worked. Log in to the VM using the `ssh` command.

Now, curl the localhost endpoint

```
curl localhost
```

You should see that the default nginx page is being served.


## Serving a custom static page

Well, the default nginx page doesnt do much for us. 
Let us get the nginx server to serve a custom html page. How about a page that says, "Hello World!" ? :)

Exit from the vagrant vm using the `exit` command.

Create a file called `index.html` in the same directory as the Vagrantfile, with the following contents.

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

Now, since this page is in the same directory as the Vagrantfile, it should be available at the path `/vagrant/index.html`.

Let us copy this over to the appropriate directory using the provisioner script, so that nginx serves this page instead of the default page.

Modify the Vagrantfile to make it look like so:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"


  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y nginx
    sudo cp /vagrant/index.html /var/www/html
  SHELL
end
```
## Provision command

Here we learn a new command called `vagrant provision`.

The provision command runs the provisioner script on VMs that have been provisioned.

Run the command

```
vagrant provision
```

Observe the output.
Here, we see that the provisioner tries to install nginx again, and finds that nginx has already been ainstalled.

Then, we can see that it copies over the `index.html` file.

Now SSH into the VM using the `vagrant ssh` command and curl the localhost endpoint

```
curl localhost
```

You can see that our new Hello World file is being served.

## Moving the provisioner script contents to a separate file.
Now for small snippets we can specify the commands inline in the Vagrantfile.

For larger files, we would prefer to have the script contents specified in a separate file.

Let us do that. Create a file called `provisioner.sh` with the following contents.

```
#!/bin/bash

apt-get update
apt-get install -y nginx
sudo cp /vagrant/index.html /var/www/html
```

Now modify the `Vagrantfile` to be as follows:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"
  config.vm.provision "shell", path: "provisioner.sh"
end
```

You can destroy and recreate the VM to ensure that this works.
Log in to the VM and curl the localhost endpoint again, to ensure that this worked as intended.

