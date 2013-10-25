import subprocess
import json
import time
import unittest

import config

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class ActionsHttpRestTestCase(BaseIntegrationTest, IntegrationTestRestMixin):
    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, config.oms_template)

    @unittest.skip('FIXME: fails by unknown reason, debug and enable')
    def test_allocate_rest(self):
        # _check_preconditions_for_allocate() should use OMS -- virsh may be not installed
        #self._check_preconditions_for_allocate()
        self.assert_rest('/machines/hangar', method='post', data=json.dumps({'backend': 'openvz'}),
                         auth=self.auth)
        self.assert_path('/machines/hangar', 'vms-openvz')

        self.assert_rest('/machines/hangar/vms-openvz', method='get')
        self.assert_rest('/machines/hangar/vms-openvz', method='post',
                         data=json.dumps({'hostname': self.rest_vm_name,
                                          'template': config.oms_template,
                                          'root_password': 'opennode',
                                          'root_password_repeat': 'opennode',
                                          'start_on_boot': 'false'}))
        time.sleep(9) # Waiting for machine to create

        vm_path = '/machines/hangar/vms-openvz/by-name/%s' % self.rest_vm_name
        self.assert_rest(vm_path + '/actions/allocate', method='put')

        self.assert_vm_rest(self.rest_vm_name)
        self.assertRaises(AssertionError, self.assert_rest, vm_path, method='get')

    @unittest.skip('TODO: write deployment integration test!')
    def test_deploy(self):
        assert False, 'TODO: write deployment integration test!'

    @unittest.skip('TODO: write deployment integration test!')
    def test_undeploy(self):
        assert False, 'TODO: write deployment integration test!'
