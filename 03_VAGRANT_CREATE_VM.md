# Creating VMs using Vagrant

We now know just enough about vagrant to start using it productively.
Let's get started.

Create a new directory called `vagrant_hello_world`, and change to that directory.

```
mkdir vagrant_hello_world
cd vagrant_hello_world
```

## Creating your first Vagrantfile

Run the following command

```
vagrant init hashicorp/bionic64
```

This command uses the "Ubuntu 18 Bionic Beaver" box that is provided by Hashicorp, the creators of vagrant.
Let us inspect the `Vagrantfile that got generated.

```
cat Vagrantfile
```

You can see that the Vagrantfile is actually a ruby snippet. A lot of code in the snippet is commented out. We can selectively uncomment them to enable certain behaviour, but let us not worry about that for now.

If you ignore the comments, the file contents are basically as follows:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "hashicorp/bionic64"
end
```

As you can see, the Vagrantfile is a [code block](https://mixandgo.com/learn/mastering-ruby-blocks-in-less-than-5-minutes) that receives an object as a block parameter in the variable named `config`.

The rest of the Vagrantfile is configuring a single property of this object.

So basically this is what Vagrantfile does. It allows the user to specify the behaviour of vagrant by allowing the user to customize the block parameter.

The Vagrant api is rich, and allows for a lot of customization. But we need not explore it right now as we will see a lot more of it in the coming chapters.

## Bringing up the VM

Let us now bring up the VM. Run the following command 

```
vagrant up
```

The first time you run this command, it will download the Ubuntu Bionic Box from the internet. Therefore it will take some time. 

But for subsequent runs, the command takes a lot less time since it caches the boxes that it downloaded during the first run. The command output is informative, and provides a lot of insight on what Vagrant does behind the scenes. But let us not worry about any of that for now.

ALl we need to know is that vagrant just spun up a VM. You can see the VM running by opening the Virtualbox GUI

![Virtualbox GUI](https://i.imgur.com/BBCNfqn.png)

## Logging into the VM

Let us now SSH into the VM. Run the following command

```
vagrant ssh
```

This should log you into the VM. Vagrant uses a user called, well, `vagrant` by default to log in users.

Take a look around. It is a standard Ubuntu VM.

## Synced folders
Vagrant has a feature called synced folders.

Go take a look at the contents of the /vagrant directory

```
ls /vagrant
```

Notice anything? The Contents of the /vagrant directory are the same as the contents of the directory which houses the `Vagrantfile`. This is because Vagrant mounts the current directory at the `/vagrant` location. This is a very useful feature that lets us supply artifacts to the VM.

Run the `df` linux command as follows:

```
df -h
```

The `df` command lets you view various file systems and some metadata about them.

Notice the following line?

```
vagrant                       234G  195G   39G  84% /vagrant`
```

Now run the `findmnt` command:

```
findmnt
```

The command lists various filesystems that are currently mounted.

Look for the following line.

```
/vagrant        vagrant     vboxsf      rw,nodev,relatime,iocharset=utf8,uid=1000,gid=1000
```

You can create files in '/vagrant` to copy them to and from the host.


## Logging out of the VM
You can exit the VM by simply logging out of the current session.

```
exit
```

## Destroying the VM

Now that we have spun up a VM, let us not get too attached to it. Remember, VMs are cattle. Not pets.

Delete the VM by running the following command:


```
vagrant destroy
```

And just like that, the VM has been deleted. 
And that is okay. 
You can spin up a new one by running the `vagrant up` command again.





