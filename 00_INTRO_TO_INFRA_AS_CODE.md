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

<img style="display: block;" src="https://live.staticflickr.com/1671/25750418554_fef67ab03b_b.jpg" alt="Puppies!"><a href="https://www.flickr.com/photos/43556229@N07/25750418554">"Puppies!"</a><span> by <a href="https://www.flickr.com/photos/43556229@N07">alasdair massie</a></span> is licensed under <a href="https://creativecommons.org/licenses/by-sa/2.0/?ref=ccsearch&atype=html" style="margin-right: 5px;">CC BY-NC-SA 2.0</a>

Pets are cute furry animals that you love. You feed them ice cream. You take cute pictures with them and post them on social media. You treat them as your family member. They are often your best friend. You cry when they die. And you promise yourself that you will never get another pet ever because *they leave us too soon man....*


Now, what do you think of when you hear the word "Cattle"?

<img style="display: block;" src="https://api.creativecommons.engineering/t/http://s0.geograph.org.uk/geophotos/04/16/39/4163993_2649e9ba.jpg" alt="Mid Devon : Cattle Grazing"><a href="http://www.geograph.org.uk/photo/4163993">"Mid Devon : Cattle Grazing"</a><span> by <a href="http://geograph.org.uk/profile/11775">Lewis Clarke</a></span> is licensed under <a href="https://creativecommons.org/licenses/by-sa/2.0/?ref=ccsearch&atype=html" style="margin-right: 5px;">CC BY-SA 2.0</a><a href="https://creativecommons.org/licenses/by-sa/2.0/?ref=ccsearch&atype=html" target="_blank" rel="noopener noreferrer" style="display: inline-block;white-space: none;margin-top: 2px;margin-left: 3px;height: 22px !important;"></a>

Well I know this term is confusing to my fellow Indians because we treat cows as pets. Or mothers. or Forefathers. Or Gods... 

But in this context, cattle are bovine creatures that you raise in large numbers for food. We are not emotionally attached to pets. We don't give them cute names,  rather we pierce  their ears with tags and assign them numbers. We raise them, feed them, fatten them up, and once they grow big enough, make biriyanis, burgers and steaks out of them.

*So why is the analogy of Cattle and pets important to Infra as code, geek*, you ask?

Well, handcrafted VMs are like pets. We care for them and tend to them lovingly. When these VMs *fall sick* we suffer along with them. When they die, we experience great misery.

When working with infrastructure, you should think of resources as cattle and not pets.
They are just means to an end. When one of them reaches the end of their utility, you discard them and raise new ones.


