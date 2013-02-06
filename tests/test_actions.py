import unittest
import subprocess

class ActionsSshTestCase(unittest.TestCase):

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

    def assert_path(self, path, itemname):
        itemlist = self.check_output_ssh(['ls', path])
        itemlist = map(lambda x: x[7:-5], itemlist.split())
        assert itemname in itemlist, 'Item \'%s\' not found in list %s' % (itemname, itemlist)

    def assert_vm(self, compute):
        vmlist = self.check_output_ssh(['ls', '/computes/by-name/'])
        vmlist = map(lambda x: x[7:-5], vmlist.split())
        assert compute in vmlist, 'Compute \'%s\' not found in OMS VM list %s' % (compute, vmlist)

    def _check_preconditions_for_allocate(self):
        vmliststr = subprocess.check_output(['virsh', 'list', '--name', '--state-running'])
        vmlist = filter(lambda s: len(s) > 0, vmliststr.splitlines())
        assert len(vmlist) >= 2, 'Must have at least 2 running VMs to choose from'

        for c in vmlist:
            self.assert_vm(c)
            self.assert_vm_template(c, 'oms-test-template')

    def test_allocate(self):
        self._check_preconditions_for_allocate()
        self.check_call_ssh(['cd /machines/hangar; mk virtualizationcontainer backend=openvz'])
        self.assert_path('/machines/hangar', 'vms-openvz')

        self.check_call_ssh(['cd /machines/hangar/vms-openvz; '
                             'mk compute hostname=testvm1 template=oms-test-template'])
        self.assert_path('/machines/hangar/vms-openvz/by-name', 'testvm1')

        self.check_call_ssh(['/machines/hangar/vms-openvz/by-name/testvm1/actions/allocate'])
        self.assert_vm('testvm1')
        self.cleanup()

    def cleanup(self):
        itemlist = self.check_output_ssh(['ls', '/machines/hangar/vms-openvz/'])
        itemlist = map(lambda x: x[7:-5], itemlist.split())

        for item in itemlist:
            if item not in ('actions', 'by-name'):
                self.check_call_ssh(['rm', '/machines/hangar/vms-openvz/%s' % (item)])

        itemlist = self.check_output_ssh(['ls', '/machines/hangar/vms-openvz/by-name/'])
        itemlist = map(lambda x: x[7:-5], itemlist.split())
        assert 'testvm1' not in itemlist, 'Found \'%s\' in list %s' % ('testvm1', itemlist)
