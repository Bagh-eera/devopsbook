# Vagrant networking

So we got a static page up and running inside the VM. That is good.

But we aren't really able to see the pages in a browser. 

Let us change that.

## Port Mapping in Vagrant

What does port mapping mean?

Port mapping in this context is when you configure virtualbox to route traffic from a particular port on the guest, to a particular port on the host.

Let us use vagrant to map ports of the VMs that we spin up, to specific ports on the host.

This is what the Vagrantfile should look like:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"

  # Add this line
  config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "0.0.0.0"

  config.vm.provision "shell", path: "provisioner.sh"
end
```

Now all the traffic on your host machine's port 8080 should be redirected to the VM's port 80.

Now open your browser and navigate to http://localhost:8080

You should see the web page open, served from the VM by the nginx server.

## SSH configuration

Run the command `ssh-config` as follows;

```
vagrant ssh-config
```

What do you see? You will see output similar to this:

```
Host default
  HostName 127.0.0.1
  User vagrant
  Port 2201
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no
  PasswordAuthentication no
  IdentityFile /Users/myusername/sandbox/devopsbook/code/chapter_03/.vagrant/machines/default/virtualbox/private_key
  IdentitiesOnly yes
  LogLevel FATAL
```

These are the parameters to the SSH command that vagrant cli invokes internally to log into the VM.
Yes, vagrant uses the SSH feature that is already available. Staying true to unix principles, it doesn't reinvent the wheel.
Pay close attention to the line that specifies the port. 

What do you think happened here?

Yes, vagrant has mapped the port 22, which is the SSH port of the host, to port 2201 which is a port on the guest.
Thus, the traffic on port 2201 gets routed to port 22 on the VM.


## Spinning up 2 VMs

Let us explore vagrant networking in a bit more detail.

What if we want to to spin up more than one VM, and enable them to talk to each other?

First of all, how do you even spin up more than one VM using Vagrant? Is it even possible?

Well yes it is. It is quite easy in fact.

Check out this Vagrantfile

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "hashicorp/bionic64"

  config.vm.define "vm1" do |config_vm1|
    config_vm1.vm.hostname = "vm1"
    config_vm1.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "0.0.0.0"
  end

  config.vm.define "vm2" do |config_vm2|
    config_vm2.vm.hostname = "vm2"
    config_vm2.vm.network "forwarded_port", guest: 80, host: 8081, host_ip: "0.0.0.0"
  end
end
```

What have we done here? We have 2 `config.vm.define` blocks, each defining a VM.

This lets vagrant know that we desire to spin up 2 VMs.

Run `vagrant up`. You can see both the VMs coming up.

If you want to bring up just one of the VMs, you can run 

```
vagrant up vm1
```

Similarly, if you want to destroy one of the VMs, you can run

```
vagrant destroy vm1
```


## Spinning up multiple VMs.
Let us refactor the Vagrantfile to be a bit more cleaner.
After all, it is just ruby code, and code can always be refactored.



Here is a clever idea. Why not read the VM configurations off a JSON file? 
This way, we can separate the code in the Vagrantfile from the configuration details of the VMs.

Let us create a JSON file named `cluster.json` with the following content:

```
{
    "nodes": [
        {
          "host_name": "web-vm",
          "guest_port": 80,
          "host_port": 8080,
          "host_ip": "127.0.0.1"
        },

        {
          "host_name": "db-vm",
          "guest_port": 80,
          "host_port": 8081,
          "host_ip": "127.0.0.1"
        }
    ]
}
```

Now, let us modify the Vagrantfile to read this JSON file.

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

nodes_config = (JSON.parse(File.read("cluster.json")))['nodes']

Vagrant.configure("2") do |config|


  nodes_config.each do |item|

    config.vm.define item["host_name"] do |vm_config|

      vm_config.vm.box = "hashicorp/bionic64"
      vm_config.vm.hostname = item["host_name"]
      vm_config.vm.network "forwarded_port", guest: item["guest_port"], host: item["host_port"], host_ip: item["host_ip"]
    end

  end

end
```

Run `vagrant up` now. You can see 2 VMs coming up.
You can now define as many VMs as you like, the only limitation is the CPU and memory available on your machine :)


## Getting the two VMs to talk to each other

So we can now spin up multiple VMs. But these VMs can form a cluster only if they talk to each other.
How can we connect these VMs together?

To connect the VMs, we need a common network and the VMs need to be connected to, and assigned an IP on this network.

TODO