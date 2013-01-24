import unittest
import subprocess

class SshTestCase(unittest.TestCase):
    def setUp(self):
        self.login = 'admin@localhost'

    def check_output_ssh(self, omsh_cmd):
        try:
            return subprocess.check_output(['ssh', self.login, '-p', '6022'] + omsh_cmd)
        except subprocess.CalledProcessError as e:
            if e.returncode != 255:
                raise
            return e.output

    def check_call_ssh(self, omsh_cmd):
        try:
            return subprocess.check_call(['ssh', self.login, '-p', '6022'] + omsh_cmd)
        except subprocess.CalledProcessError as e:
            if e.returncode != 255:
                raise
            return e.returncode

    def assert_vm_template(self, compute, template_name):
        assert self.check_output_ssh(['ls', '/machines/by-name/%(compute)s'
                                      '/templates/by-name/%(template)s' %
                                       {'compute': compute, 'template': template_name}])

    def assert_vm(self, compute):
        vmlist = self.check_output_ssh(['ls', '/machines/by-name/'])
        vmlist = map(lambda x: x[7:-5], vmlist.split())
        assert compute in vmlist, 'Compute \'%s\' not found in OMS VM list %s' % (compute, vmlist)

    def _check_preconditions_for_allocate(self):
        # 1. assert that we have 2 VMs ready
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            # 2. assert that we have a VM template
            self.assert_vm_template(c, 'oms-test-template')

    def test_allocate_ssh(self):
        self._check_preconditions_for_allocate()
        # 3. create a Compute under hangar with that template
        self.check_call_ssh(['cd /machines/hangar/vms-openvz; '
                             'mk hostname=testvm1 template=oms-test-template'])
        # 4. execute the action, assert expectations
        self.check_call_ssh(['/machines/hangar/vms-openvz/by-name/testvm1/actions/allocate'])
        self.assert_vm('testvm1')
