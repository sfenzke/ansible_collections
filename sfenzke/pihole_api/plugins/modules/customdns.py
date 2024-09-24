#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: customdns

short_description: This is a module to configure customdns of a pihole installation.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description:
    This moduleconfigures customdns entrie of a pihole installation.

options:
    api_key:
        description:
            The api key to authenticate against the pihole server.
            Can also be set via PIHOLE_API_KEY environmaent variable
        required: true
        type: str
    url:
        description:
            URL the pihole server is listening on.
            Can also be give via PIHOLE_URL Eenvironment variable.
        required: true
        type: str
    domain:
        description:
            domain to add
        required: true
        type: str
    ip:
        description:
            IP to add
        required: true
        type: str
    reload:
        description:
            Whether the DNS Service should be reloadedafterthechanges have been applied.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Stefan Fenzke (@sfenzke)
'''

EXAMPLES = r'''
# creatte a newentr
- name: Create new customdnsentr
  sfenzke.pihole_api.customdns:
    url: http://example.org
    ip: 192.168.0.1
    state: present
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
api_url:
    description: The given api_url.
    type: str
    returned: always
    sample: 'http://example.org'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.parameters import env_fallback

import requests

params = {}
api_url = ''


def build_params_string(params):
    return '&'.join([k if v is None else f'{k}={v}' for k, v in params.item()])


def is_present(domain, ip):
    local_params = params.copy()

    local_params['action'] = 'get'

    custom_dns_entries = [(item[0], item[1]) for item in requests.get(api_url, build_params_string(local_params)).json()['data']]

    return (domain, ip) in custom_dns_entries


""" Execute the command.

    Parameters:
    domain: the domain to add
    ip: the ip to add
    reload: whether the DNS service should be reoalded afterthe update
    check_mode: whether the module is running in check mode. defaults to False

    Returns:
    bool: False if no change has been mad otherwise True
"""


def execute_request(domain, ip, reload, check_mode=False):
    if (is_present(domain, ip) and params['action'] == 'add') or (not is_present(domain, ip) and params['action'] == 'delete'):
        return False

    local_params = params.copy()
    local_params['ip'] = ip
    local_params['domain'] = domain
    local_params['reload'] = reload

    if not check_mode:
        requests.get(api_url, build_params_string(local_params))

    return True


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = {
        'api_key': {
            'type': 'str',
            'required': True,
            'fallback': (env_fallback, 'PIHOLE_API_KEY')},
        'url': {
            'type': 'str',
            'required': True,
            'fallback': (env_fallback, 'PIHOLE_URL')},
        'ip': {
            'type': 'str',
            'required': True},
        'domain': {
            'type': 'str',
            'required': True},
        'reload': {
            'type': 'bool',
            'required': 'false',
            'default': True},
        'state': {
            'type': 'str',
            'required': False,
            'default': 'present',
            'choices': ['present', 'absent']},
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    api_url = f'{module.params["url"]}/admin/api'

    params['auth'] = module.params['api_key']
    params['customdns'] = None

    if module.params['state'] == 'present':
        params['action'] = "add"
    else:
        params['action'] = 'delete'

    changed = execute_request(module.params['domain'],
                              module.params['ip'],
                              module.params['reload'],
                              module.check_mode)

    result = dict(
        changed=changed,
        api_url=api_url
    )

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
