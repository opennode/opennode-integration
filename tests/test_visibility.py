import subprocess
import json

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class VisibilityTestCase(BaseIntegrationTest, IntegrationTestRestMixin):
    # Not used in this class?
    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, 'oms-test-template')

    def test_user_undeployed_vm_visibility(self):
        self.assert_rest('/machines/by-name/ondev/vms', method='post',
                         data=json.dumps({'hostname': 'test2rest',
                                          'template': 'oms-test-template',
                                          'start_on_boot': False,
                                          'root_password': 'a',
                                          'root_password_repeat': 'a'}),
                         auth=('a', 'a'))
        self.assert_no_vm_rest('test2rest', auth=('b', 'b'))

    def test_user_hangar_vm_visibility(self):
        self.assert_rest('/machines/hangar', method='post',
                         data=json.dumps({'backend': 'openvz'}),
                         auth=self.auth)
        self.assert_path('/machines/hangar', 'vms-openvz')
        self.assert_rest('/machines/hangar/vms-openvz', method='get', auth=self.auth)
        self.assert_rest('/machines/hangar/vms-openvz', method='post',
                         data=json.dumps({'hostname': 'test3rest',
                                          'template': 'oms-test-template',
                                          'root_password': 'opennode',
                                          'root_password_repeat': 'opennode',
                                          'start_on_boot': 'false'}), auth=('a', 'a'))
        self.assert_no_hangar_compute_rest('test3rest', auth=('b', 'b'))
