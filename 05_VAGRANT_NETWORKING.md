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


So, let us first create a network in virtualbox that the VMs can connect to.

Find the Host Network Manager menu for Virtualboc and create a new Adapter. 
This is what the adapter configuration should look like:

![Adapter Configuration](https://i.imgur.com/PyPaauj.png)

We will now need to create a second network card on our VMs that will connect to this network.

Modify the JSON File called `cluster.json` so that it contains the following content.

```
{
    "nodes": [
        {
            "host_name": "web-vm",
            "port_mappings": [
                { "guest_port": 80, "host_port": 8083, "host_ip": "127.0.0.1" },
                { "guest_port": 443, "host_port": 14433, "host_ip": "127.0.0.1" }
            ],
            "network_configs": [
                { "ip": "192.167.32.3", "name": "vboxnet0", "adapter": 2 }
            ]
        },
        {
            "host_name": "data-vm",
            "port_mappings": [
                { "guest_port": 80, "host_port": 8084, "host_ip": "127.0.0.1" },
                { "guest_port": 443, "host_port": 14434, "host_ip": "127.0.0.1" }
            ],
            "network_configs": [
                { "ip": "192.167.32.4", "name": "vboxnet0", "adapter": 2 }
            ]
        }
    ]
}
```

Notice the different configurations specified in the json file

* The json file has an array of objects under the key `nodes`
* Each object in the array has 3 keys: `host_name`, `port_mappings` and `network_configs`.
* The `port_mappings` key is an array that lists all port mappings. Currently we have 2 ports mapped for each VM.
* The `network_configs` key is an array that list all the network configurations. Currently we have 1 network configuration.

Now modify the Vagrantfile so that itv reads the configuration JSON and applies them appropriately.
It should contain the collowing content:

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
end
```

Understand what the Vagrantfile does differently now.

* It configures the VMs to use 1 CPU and 512 MB of memory
* It loops through all port mappings and configures the port forwardings between the VMs and the host
* It loops through all the network configurations and configures the network appropriately.


Now bring up the VMs using the  `vagrant up` command.
Check that both VMs have come up using the `vagrant status` command

```
vagrant status
```
It should present an output like this:

```
Current machine states:

web-vm                    running (virtualbox)
data-vm                   running (virtualbox)

This environment represents multiple VMs. The VMs are all listed
above with their current state. For more information about a specific
VM, run `vagrant status NAME`.
```

Now login to one of `web-vm` using the command

```
vagrant ssh web-vm
```

Now, inside the VM, run the command to view the network configuration

```
ip addr
```

Pay attention to this part of the output

```
3: eth1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 08:00:27:3a:57:d5 brd ff:ff:ff:ff:ff:ff
    inet 192.167.32.3/24 brd 192.167.32.255 scope global eth1
       valid_lft forever preferred_lft forever
    inet6 fe80::a00:27ff:fe3a:57d5/64 scope link
       valid_lft forever preferred_lft forever
```

We can see that a second network adapter has been configured and it has the IP address `192.167.32.3`.

Exit the VM using the `exit` command and repeat the same steps in the `data-vm`.

Now, the two VMs should be able to communicate over a network.
Let us see that in action.

1. SSH into the `web-vm` using the `vagrant ssh web-vm` command
2. Run the following command `netcat -l 4444`. The netcat command will listen to port 4444 and block.
3. Open a new terminal window and navigate to the folder containing the Vagrantfile
4. SSH into the `data-vm` using the `vagrant ssh data-vm` command
5. Now run the command `netcat 192.167.32.3 4444` to start communicating to the `web-vm`. This command will block input
6. Now type messages into the `data-vm` terminal window. Type in any random strings.
7. You can see that the messages start appearing in the `web-vm` terminal.
8. Press Ctrl+C to exit. The commands on both the terminals will exit.

![Communicating between two VMs](https://i.imgur.com/0VpVYfc.png)


So there we have it. We can now set up clusters and have them communicate to each other.
With just enough knowledge about Vagrant, we can be productive. 

Let us now see how we can configure the VMs in a more sophisticated manner.
How about setting up a simple web app with a web server running on one VM and a database running on another?
Should be doable, right? We will do just that when we explore configuration management with Ansible.

