import httplib
import requests
import subprocess
import unittest
import logging

import config

httplib.HTTPConnection.debuglevel = 1

class IntegrationTestRestMixin(object):

    def assert_rest(self, path, method='get', data=None, auth=None):
        method = getattr(requests, method)
        r = method('http://%s%s' % (self.host, path), data=data,
                   auth=(auth or getattr(self, 'auth', None)))
        r.raise_for_status()
        data = r.json()
        logging.debug("Response JSON: %s" % data)
        if 'success' in data:
            self.assertEqual(True, data['success'])
        return data

    def assert_vm_rest(self, compute, auth=None):
        r = requests.get('http://%s/computes/by-name/%s?depth=1&attrs=hostname' % (self.host, compute),
                         auth=(auth or getattr(self, 'auth')))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(compute, data['hostname'])
        return data

    def assert_no_vm_rest(self, compute, auth=None):
        r = requests.get('http://%s/computes/by-name/%s?depth=1&attrs=hostname' % (self.host, compute),
                         auth=(auth or getattr(self, 'auth')))
        assert r.status_code is 404, 'Compute %s is visible in computes!' % (compute)

    def assert_hangar_compute_rest(self, compute, auth=None):
        r = requests.get('http://%s/machines/hangar/by-name/%s?depth=1&attrs=hostname'
                         % (self.host, compute),
                         auth=(auth or getattr(self, 'auth')))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(compute, data['hostname'])

    def assert_no_hangar_compute_rest(self, compute, auth=None):
        r = requests.get('http://%s/machines/hangar/by-name/%s?depth=1&attrs=hostname'
                         % (self.host, compute),
                         auth=(auth or getattr(self, 'auth')))
        logging.debug("Resonse HTTP status: %d" % r.status_code)
        assert r.status_code == 404, 'Compute %s is visible in hangar!' % (compute)

    def assert_vm_template_rest(self, compute, template, auth=None):
        r = requests.get('%s/machines/by-name/%s/templates/by-name/%s' %
                         (self.base_address, compute, template),
                         auth=(auth or getattr(self, 'auth')))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(template, data['name'])


class BaseIntegrationTest(unittest.TestCase):
    rest_vm_name = 'test1rest'
    ssh_vm_name = 'test1ssh'

    def setUp(self):
        self.login = config.admin_user
        self.password = config.admin_password
        self.auth = (self.login, self.password)
        self.host = '%s%s' % (config.oms_hostname_http,
                              ':' + config.oms_port_http if config.oms_port_http else '')
        self.ssh_cmd = ['ssh', '%s@%s' % (self.login, config.oms_hostname_ssh), '-p', config.oms_port_ssh]

    def tearDown(self):
        self.cleanup()

    def ssh(self, omsh_cmd):
        try:
            command_to_run = self.ssh_cmd + omsh_cmd
            logging.debug("Executing: %s " % command_to_run)
            p = subprocess.Popen(self.ssh_cmd + omsh_cmd,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            if p.returncode != 0:
                raise subprocess.CalledProcessError(p.returncode, omsh_cmd, p.stdout.read())
            stderr = p.stderr.read()
            assert not stderr, stderr
            stdout = p.stdout.read()
            logging.debug("Stdout: %s" % stdout)
            return stdout
        except subprocess.CalledProcessError as e:
            assert e.returncode == 255, e.output
            logging.debug("Stderr: %s (code: %d)" % (e.output, e.returncode))
            return e.output

    def get_itemlist(self, path):
        itemlist = self.ssh(['ls', path])
        return map(lambda x: x[7:-5], itemlist.split())

    def assert_vm_template(self, compute, template_name):
        assert self.ssh(['ls', '/machines/by-name/%(compute)s'
                         '/templates/by-name/%(template)s' %
                         {'compute': compute, 'template': template_name}])[0], \
               'Template \'%s\' was not found' % template_name

    def assert_path(self, path, itemname):
        itemlist = self.get_itemlist(path)
        assert itemname in itemlist, 'Item \'%s\' not found in list %s' % (itemname, itemlist)

    def assert_vm(self, compute):
        vmlist = self.get_itemlist('/computes/by-name/')
        assert compute in vmlist, 'Compute \'%s\' not found in OMS VM list %s' % (compute, vmlist)

    def assert_no_vm(self, compute):
        self.assertRaises(AssertionError, self.assert_vm, compute)

    def cleanup(self):
        itemlist = self.get_itemlist('/machines/hangar/vms-openvz/')

        for item in itemlist:
            if item not in ('actions', 'by-name'):
                logging.debug("Deleting machine %s from hangar" % (item))
                self.ssh(['rm', '/machines/hangar/vms-openvz/%s' % (item)])

        mlist = self.get_itemlist('/machines/')

        for m in mlist:
            if m not in ('actions', 'by-name', 'incoming'):
                itemlist = self.get_itemlist('/machines/%s/vms/' % (m))
                for item in itemlist:
                    if item not in ('actions', 'by-name', '88888888-4444-4444-4444-cccccccccccc'):
                        # FIXME machine should only be removed if its hostname is not oms.test
                        # with that we can drop 'magic UUID' 888...ccc -- see above
                        logging.debug("Deleting machine %s from HN %s" % (item, m))
                        self.ssh(['rm', '/machines/%s/vms-openvz/%s' % (m, item)])

        vmlist = self.get_itemlist('/machines/hangar/vms-openvz/by-name/')
        assert self.ssh_vm_name not in vmlist, 'Found \'%s\' in hangar list %s' % (self.ssh_vm_name, vmlist)
        self.assert_no_vm(self.ssh_vm_name)
