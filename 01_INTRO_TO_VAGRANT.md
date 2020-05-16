# Introduction to Vagrant

## What is Vagrant?
Vagrant is a tool that makes it easy to spin up new Virtual Machines.
With Vagrant, you can create, configure and deploy new virtual machines using some code and command lines.


## Why is Vagrant so cool?
Vagrant makes it easy to spin up, configure and destroy VMs. 

The removal of friction when it comes to managing Virtual Machines makes it easy to treat the VMs as Cattle instead of pets.

I personally find Vagrant to be the gateway drug for DevOps. And a useful tool in the arsenal of any DevOps Engineer.



## Installing Vagrant

### Prerequisites
Vagrant uses VirtualBox to provision VMs by default. So you need virtualbox to learn how to use Vagrant. Head over to [VirtualBox Downloads page](https://www.virtualbox.org/wiki/Downloads) and grab the latest installer.

Depending on the current state of your machine, you might have to tweak the bios settings to enable virtualization. You might have to google for instructions specific to your computer. Here is an example article for how to do it on certain computers: https://www.howtogeek.com/213795/how-to-enable-intel-vt-x-in-your-computers-bios-or-uefi-firmware/

Instructions for your personal hardware may vary.



### On Mac OS X
Installing Vagrant on Mac OS X is pretty straightfoward.

Download the *.dmg installer from the [Vagrant downloads page](https://www.vagrantup.com/downloads.html) and run it.


### On Linux
Installing Vagrant on Linux is pretty straightfoward.

Download the installer from the [Vagrant downloads page](https://www.vagrantup.com/downloads.html) and run it. 

For Debian and Debian Based OSes like Ubuntu, Linux Mint, etc download the *.deb package and install it using the appropriate command.


For Centos and other Red Hat family of OSes, download the rpm file and install it using the appropriate command.

### On Windows 10
Unlike Linux or Mac which are unix based, getting Vagrant and virtualbox working for the purposes of working through exercises in this book is somewhat hairy.

Fortunately due to Microsoft's recent adoption of Open Source and Linux, it is becoming easier than before to work with opensource tools like Vagrant.

Windows 10 has a feature called WSL which lets you run a Linux environment inside Windows 10.

Here is what we are going to do:

We are going to run Virtualbox on Windows host, and install vagrant on the WSL guest.

Then we are going to configure the Vagrant setup inside WSL to use the virtualbox on the host.

Here is what you need to do:

1. Enable WSL 2
2. Install Vagrant on the WSL 2 
3. Set some environment variables to let vagrant use the virtualbox on Windows Host.
4. Create a firewall rule to allow traffic from WSL to access ports of VMs running on virtualbox 


#### Enabling WSL 2
Follow the documentation link here:
https://docs.microsoft.com/en-us/windows/wsl/install-win10

Warning: This may require you to sign up for Microsoft's Insider Program and run updates.
Running updates will take time and consume your internet bandwidth.

#### Install Vagrant on WSL 2
Vagrant must be installed INSIDE the WSL linux distribution. 

Download the installer from the [Vagrant downloads page](https://www.vagrantup.com/downloads.html) using wget. 

For Debian and Debian Based OSes like Ubuntu, Linux Mint, etc download the *.deb package and install it using the appropriate command.


For Centos and other Red Hat family of OSes, download the rpm file and install it using the appropriate command.

#### Set environment variables to let vagrant use the virtualbox on Windows Host.
Set the following environment variables in your `.bashrc` file (Or the equivalent startup file for the shell of your choice)

```
export VAGRANT_WSL_ENABLE_WINDOWS_ACCESS="1"
export PATH="$PATH:/mnt/c/Program Files/Oracle/VirtualBox"
export VAGRANT_WSL_WINDOWS_ACCESS_USER_HOME_PATH="/mnt/c/Users/myusername/vagrantwsl"
```

#### Creating a firewall rule
Depending upon your configuration, Windows does not allow programs running in the WSL environment to access ports on the host. For this reason, you may need to create a firewall rule that allows access.

Run the following powershell command to create a firewall rule that allows traffic from WSL.

```
New-NetFirewallRule -DisplayName "WSL" -Direction Inbound  -InterfaceAlias "vEthernet (WSL)"  -Action Allow
```

### Gotchas while using Vagrant on WSL

Vagrant's support for WSL is a [work in progress](https://www.vagrantup.com/docs/other/wsl.html). For this reason, you need to mindful of some things that may not work or some additional configurations that may be required.

TODO

#### Disable UART Mode

#### Synced folders will not work

#### IP to be used in order to SSH

