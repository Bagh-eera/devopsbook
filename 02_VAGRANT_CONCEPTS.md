# Vagrant Concepts

Vagrant is simple but feature rich, with a very easy learning curve.
Let us look at a concepts that you need to understand to be productive with Vagrant.

Vagrant has [comprehensive, easy to understand documentation](https://www.vagrantup.com/docs/) so it is pointless to duplicate that information here.

The intention of this chapter is to introduce you to just enough concepts to make you productive with Vagrant.

## Vagrantfile
Vagrant is written in Ruby.

Vagrantfile is a ruby script that you supply in order to specify the VM configuration that you are trying to provision. 

Vagrant makes it easy to create the Vagrantfile by providing the `init` command that creates a default file for you.


## Vagrant boxes
Vagrant works by downloading prebuilt VM images called vagrant "boxes". 

You can discover publicly available boxes by browsing the [boxes gallery](https://app.vagrantup.com/boxes/search) provided by vagrant. Here you can find a lot of open source boxes that are built by various software organizations and open source communities.

Given the popularity of Vagrant, it is not unusual to find the perfect pre-packaged box that does exactly what you need. But as is the case with any open source library, caution should be exercised when downloading boxes off the internet. Always use boxes from highly trusted publishers only. Also, try to go through the source code of the boxes in order to verify them.




## Vagrant providers
Providers are the hypervisors that provide the virtualization features required to spin up VMs. By default, Vagrant uses virtualbox as the provider. But you can configure Vagrant to use a variety of other providers like VMWare WorkStation, Hyper-V  and even cloud providers like AWS, Azure, GCP, etc.


## Vagrant provisioners
Priovisioners are basically mechanisms that allow you to configure the Virtual Machines right after you have spun them up. 

The provisioner that is easiest to use is a shell script. Vagrant lets you specify a shell script that will run inside the VM that you just spun up. You can use this shell script to modify the VM in any way you like; like creating files and directory structures, installing packages, running commands etc.


Vagrant also provides a variety of more sophisticated provisioners such as Ansible, Puppet, Chef, Salt etc.

