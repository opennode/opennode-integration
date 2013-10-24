import subprocess
import json
import unittest

import config

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class VisibilityTestCase(BaseIntegrationTest, IntegrationTestRestMixin):
    # Not used in this class?
    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, config.oms_template)

    def test_user_undeployed_vm_visibility(self):
        self.assert_rest('/machines/by-name/ondev/vms', method='post',
                         data=json.dumps({'hostname': 'test2rest',
                                          'template': config.oms_template,
                                          'start_on_boot': False,
                                          'root_password': 'a',
                                          'root_password_repeat': 'a'}),
                         auth=('a', 'a'))
        self.assert_no_vm_rest('test2rest', auth=('b', 'b'))

    @unittest.skip('FIXME: fails by unknown reason')
    def test_user_hangar_vm_visibility(self):
        # Admin can create new backend
        self.assert_rest('/machines/hangar', method='post',
                         data=json.dumps({'backend': 'openvz'}),
                         auth=self.auth)
        self.assert_path('/machines/hangar', 'vms-openvz')

        # Unprivileged user can view backend
        self.assert_rest('/machines/hangar/vms-openvz', method='get', auth=('a', 'a'))

        # Admin can create new machines
        self.assert_rest('/machines/hangar/vms-openvz', method='post',
                         data=json.dumps({'hostname': 'test3rest',
                                          'template': config.oms_template,
                                          'root_password': 'opennode',
                                          'root_password_repeat': 'opennode',
                                          'start_on_boot': 'false'}), auth=self.auth)

        # Unprivileged user cannot view machines created by admin
        self.assert_no_hangar_compute_rest('test3rest', auth=('a', 'a'))
