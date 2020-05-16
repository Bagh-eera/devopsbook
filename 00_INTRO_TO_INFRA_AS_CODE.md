# Infrastructure as Code

## What is Infrastructure?

Basically, software infrastructure is components that provide the following 3 features:

* Compute
* Storage
* Network

## Introduction to Infrastructure as Code

The Infrastructure as code is basically the act of using programmatic concepts to define Compute, storage and Network components.

THink about how you typically configure your software infrastructure.

Typically, you create a VM by using a GUI application provided by your hypervisor. 
This can be a desktop based software, like Vmware Workstation, Oracle VirtualBox, etc.
Or this can be a sophisticated web portal provided by one of the cloud providers, like AWS, GCP, Azure etc.

Configuring infrastructure using a GUI application involves a lot of pointing and clicking.

And once you create a VM, you then configure it manually. i.e. you open up a remote desktop window, you point and click around, install a bunch of software, etc. Or you ssh into the VM, run a bunch of commands, scripts, etc.

The act creating and configuring a VM manually can be termed "handcrafting". 

Handcrafting a VM makes the VM pretty unique and hard/impossible to reconstruct.

At best you would create elaborate documentation to document how you created the VM.
As is the case with all documentation, it tends to decay and get outdated.
Maintaining up to date documentation is not something every team cares about.

Over a period of time, when the documentation gets outdated, you slowly stop relying on the document. Rather, you rely on the person who created the VM. You rely on his memory, his recollection of what he did to bring the VM to the state it is currently in.

Now what happens when the person who created the VM leaves the company? You are left with second hand information of how the VMs were configured. This can be termed "tribal knowlege". Think of tales of yore, legends, mythologies. Stories that are passed from generation to generation, evolving and mutating through time.  Good for fairy tales. Bad for organizations that depend on software to run reliably.


## Cattle vs pets.

One of the primary tenants of good devops practices is  treating servers as "cattle and not pets".


What do you think of when you hear the word "Pets"?

![Pets](https://i.redd.it/7e7lol4ox0b01.jpg)

Pets are cute furry animals that you love. You feed them ice cream. You take cute pictures with them and post them on social media. You treat them as your family member. They are often your best friend. You cry when they die. And you promise yourself that you will never get another pet ever because *they leave us too soon man....*


Now, what do you think of when you hear the word "Cattle"?

![Cattle](https://i.imgur.com/vxEBriy.jpg)

Well I know this term is confusing to my fellow Indians because we treat cows as pets. Or mothers. or Forefathers. Or Gods... 

But in this context, cattle are bovine creatures that you raise in large numbers for food. We are not emotionally attached to pets. We don't give them cute names,  rather we pierce  their ears with tags and assign them numbers. We raise them, feed them, fatten them up, and once they grow big enough, make biriyanis, burgers and steaks out of them.

*So why is the analogy of Cattle and pets important to Infra as code, geek*, you ask?

Well, handcrafted VMs are like pets. We care for them and tend to them lovingly. When these VMs *fall sick* we suffer along with them. When they die, we experience great misery.

When working with infrastructure, you should think of resources as cattle and not pets.
They are just means to an end. When one of them reaches the end of their utility, you discard them and raise new ones.


