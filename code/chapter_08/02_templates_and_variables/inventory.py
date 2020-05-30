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
                    'ansible_private_key_file': '.vagrant/machines/web-01/virtualbox/private_key',
                    'bind_address': 'localhost',
                    'bind_port': '5000'
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
