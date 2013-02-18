import subprocess

from integration_test_base import BaseIntegrationTest

class ActionsSshTestCase(BaseIntegrationTest):

    def test_id(self):
        output = self.ssh(['id'])
        lines = output.splitlines()
        self.assertEquals('user:', lines[0].split(' ')[0])
        self.assertEquals('admin', lines[0].split(' ')[1])
        self.assertEquals('groups:', lines[1].split(' ')[0])
        self.assertEquals('admins', lines[1].split(' ')[1])
        self.assertEquals('effective_principals:', lines[2].split(' ')[0])
        self.assertEquals('admin', lines[2].split(' ')[1])
        self.assertEquals('admins', lines[2].split(' ')[2])

    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, 'oms-test-template')

    def test_allocate(self):
        self._check_preconditions_for_allocate()
        self.ssh(['cd /machines/hangar; mk virtualizationcontainer backend=openvz'])
        self.assert_path('/machines/hangar', 'vms-openvz')

        self.ssh(['cd /machines/hangar/vms-openvz; '
                  'mk compute hostname=testvm1ssh template=oms-test-template'])
        self.assert_path('/machines/hangar/vms-openvz/by-name', 'testvm1ssh')

        self.ssh(['/machines/hangar/vms-openvz/by-name/testvm1/actions/allocate'])
        self.assert_vm('testvm1ssh')
