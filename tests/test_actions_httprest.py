import subprocess
import json

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class ActionsHttpRestTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    def tearDown(self):
        pass

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
        self.assert_rest('/machines/hangar/vms', method='get')
        self.assert_rest('/machines/hangar/vms-openvz', method='get')
        self.assert_rest('/machines/hangar/vms-openvz', method='put',
                         data=json.dumps({'hostname': 'testvm1rest', 'template': 'oms-test-template'}))
        #self.assert_rest('/machines/hangar/vms-openvz/by-name/testvm1/actions/allocate', method='put')
        self.assert_vm('testvm1rest')
        self.assert_rest('', method='delete')
