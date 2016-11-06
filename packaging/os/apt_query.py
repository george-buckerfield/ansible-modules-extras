#!/usr/bin/python

DOCUMENTATION = '''
---
module: apt_query
short_description: Query the installation status of packages using Apt.
description:
    - Returns the installation status and version number of a given package using Apt.
options:
    name:
        description:
          - A package name, like C(foo), or C(all) to return a list of all installed packages.
        required: true
        default: null
        aliases: [ 'pkg', 'package' ]
requirements:
   - python-apt
   - aptitude
author: "George Buckerfield"
notes:
'''
EXAMPLES = '''
- apt_query:
        name: "{{ item }}"
      with_items:
        - openssl
        - aptitude
        - lolcat
      register: status

    - debug: msg={{ status }}

    - apt:
        name: "{{ item.item }}"
        state: present
      become: yes
      when: not item.installed
      with_items: "{{ status.results }}"

    - name: check if apache is installed
      apt_query:
        name: apache2
      register: status

    - debug: msg={{ status }}

    - name: install apache if not present
      apt:
        name: apache2
        state: present
      become: yes
      when: not status.installed
'''

from ansible.module_utils.basic import AnsibleModule
import apt
import json

def main():
    
    module = AnsibleModule(
        argument_spec = dict(
            package = dict(default=None, aliases=['pkg', 'name'], type='str')
            ),
        required_one_of = [['name']]
        )

    cache = apt.Cache()
    packages = {}
    package = module.params['package']
    
    try:
        if package == "all":
            for pkg in apt.Cache():
                if cache[pkg.name].is_installed:
                    pkgver = cache[pkg.name].installed
                    packages[pkg.name] = pkgver.version
            response = json.dumps(packages,sort_keys=True)
            module.exit_json(changed=False, package_info=response)
        else:
            if cache[package].is_installed:
                pkgver = cache[package].installed
                packages[package] = pkgver.version
                response = json.dumps(packages,sort_keys=True)
                installed = True
            else:
                response = json.dumps({package: "not installed"})
                installed = False
            module.exit_json(changed=False, package_info=response, installed=installed)
    except KeyError:
        module.fail_json(msg="The package '%s' was not found in the apt-cache" % package)
if __name__ == '__main__':
    main()