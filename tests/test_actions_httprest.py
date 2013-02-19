import subprocess
import json

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class ActionsHttpRestTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, 'oms-test-template')

    def test_allocate(self):
        self._check_preconditions_for_allocate()
        self.assert_rest('/machines/hangar', method='post', data=json.dumps({'backend': 'openvz'}))
        self.assert_path('/machines/hangar', 'vms-openvz')
        self.assert_rest('/machines/hangar/vms-openvz', method='get')
        self.assert_rest('/machines/hangar/vms-openvz', method='post',
                         data=json.dumps({'hostname': 'testvm1rest',
                                          'template': 'oms-test-template',
                                          'root_password': 'opennode',
                                          'root_password_repeat': 'opennode',
                                          'start_on_boot': 'false'}))
        self.assert_rest('/machines/hangar/vms-openvz/by-name/testvm1rest/actions/allocate', method='put')
        self.assert_vm_rest('testvm1rest')
