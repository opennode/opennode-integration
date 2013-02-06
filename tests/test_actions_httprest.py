import unittest
import subprocess
import requests
import json

class ActionsHttpRestTestCase(unittest.TestCase):

    def setUp(self):
        self.login = 'admin'
        self.password = 'opennode'
        self.base_address = 'http://localhost:8080'

    def assert_rest(self, path, method='get', data=None):
        method = getattr(requests, method)
        r = method('%s%s' % (self.base_address, path), data=data)
        self.assertEqual(200, r.status_code)

    def assert_vm(self, compute):
        r = requests.get('%s/machines/by-name/%s' % (self.base_address, compute))
        self.assertEqual(200, r.status_code)
        data = r.json()
        self.assertEqual(compute, data['hostname'])

    def assert_vm_template(self, compute, template):
        r = requests.get('%s/machines/by-name/%s/templates/by-name/%s' % (self.base_address,
                                                                          compute, template))
        self.assertEqual(200, r.status_code)
        data = r.json()
        self.assertEqual(template, data['name'])

    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, 'oms-test-template')

    def test_allocate(self):
        self._check_preconditions_for_allocate()
        self.assert_rest('/machines/hangar', method='put', data=json.dumps({'backend': 'openvz'}))
        self.assert_rest('/machines/hangar/vms-openvz', method='put',
                         data=json.dumps({'hostname': 'testvm1', 'template': 'oms-test-template'}))
        #self.assert_rest('/machines/hangar/vms-openvz/by-name/testvm1/actions/allocate', method='put')
        self.assert_vm('testvm1')
        self.assert_rest('', method='delete')
