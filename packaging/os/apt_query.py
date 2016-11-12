#!/usr/bin/python

DOCUMENTATION = '''
---
module: apt_query
short_description: Query the installation status of packages using Apt.
description:
    - Returns the installation status and version number of a given package using Apt, or versions for all installed packages. 
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
# Check the installed version of openssl
- apt_query:
    name: openssl
  register: query

# Display the version
- debug: msg="{{ query.package_info['openssl'] }}"

# Do something if the version doesn't match a requirement
- name: update openssl if necessary
  apt:
    name: openssl
    state: latest
  become: yes
  when: query.package_info['openssl'] != "1.0.1f-1ubuntu2.21"
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
            module.exit_json(changed=False, package_info=packages)
        else:
            if cache[package].is_installed:
                pkgver = cache[package].installed
                packages[package] = pkgver.version
                installed = True
            else:
                packages[package] = ""
                installed = False
            module.exit_json(changed=False, package_info=packages, installed=installed)
    except KeyError:
        installed = False
        module.exit_json(msg="The package '%s' was not found in the apt-cache" % package, installed=installed)
if __name__ == '__main__':
    main()