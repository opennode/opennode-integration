import requests
import subprocess
import unittest


class IntegrationTestRestMixin(object):

    def assert_rest(self, path, method='get', data=None):
        method = getattr(requests, method)
        r = method('%s%s' % ('http://%s:8080' % self.host, path), data=data)
        r.raise_for_status()
        data = r.json()
        if 'success' in data:
            self.assertEqual(True, data['success'])

    def assert_vm_rest(self, compute):
        r = requests.get('http://%s:8080/computes/by-name/%s?depth=1&attrs=hostname' % (self.host, compute))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(compute, data['hostname'])

    def assert_vm_template_rest(self, compute, template):
        r = requests.get('%s/machines/by-name/%s/templates/by-name/%s' %
                         (self.base_address, compute, template))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(template, data['name'])


class BaseIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.login = 'admin'
        self.host = 'localhost'

    def tearDown(self):
        self.cleanup()

    def ssh(self, omsh_cmd):
        try:
            p = subprocess.Popen(['ssh', '%s@%s' % (self.login, self.host), '-p', '6022'] + omsh_cmd,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                raise subprocess.CalledProcessError(p.returncode, omsh_cmd, p.stdout.read())
            stderr = p.stderr.read()
            assert not stderr, stderr
            return p.stdout.read()
        except subprocess.CalledProcessError as e:
            assert e.returncode == 255, e.output
            return e.output

    def get_itemlist(self, path):
        itemlist = self.ssh(['ls', path])
        return map(lambda x: x[7:-5], itemlist.split())

    def assert_vm_template(self, compute, template_name):
        assert self.ssh(['ls', '/machines/by-name/%(compute)s'
                         '/templates/by-name/%(template)s' %
                         {'compute': compute, 'template': template_name}])[0],\
               '%s was not found' % template_name

    def assert_path(self, path, itemname):
        itemlist = self.get_itemlist(path)
        assert itemname in itemlist, 'Item \'%s\' not found in list %s' % (itemname, itemlist)

    def assert_vm(self, compute):
        vmlist = self.get_itemlist('/computes/by-name/')
        assert compute in vmlist, 'Compute \'%s\' not found in OMS VM list %s' % (compute, vmlist)

    def cleanup(self):
        itemlist = self.get_itemlist('/machines/hangar/vms-openvz/')

        for item in itemlist:
            if item not in ('actions', 'by-name'):
                self.ssh(['rm', '/machines/hangar/vms-openvz/%s' % (item)])

        mlist = self.get_itemlist('/machines/')

        for m in mlist:
            if m not in ('actions', 'by-name', 'incoming'):
                itemlist = self.get_itemlist('/machines/%s/vms/' % (m))
                for item in itemlist:
                    if item not in ('actions', 'by-name'):
                        self.ssh(['rm', '/machines/%s/vms-openvz/%s' % (m, item)])

        vmlist = self.get_itemlist('/machines/hangar/vms-openvz/by-name/')
        assert 'testvm1ssh' not in vmlist, 'Found \'%s\' in hangar list %s' % ('testvm1ssh', vmlist)

        self.assertRaises(AssertionError, self.assert_vm, 'testvm1ssh')
