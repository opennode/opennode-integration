import subprocess
import json
import logging
import unittest

import config

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class VisibilityTestCase(BaseIntegrationTest, IntegrationTestRestMixin):
    @unittest.skip('TODO: Move visibility tests to a separate suite')
    def test_user_undeployed_vm_visibility(self):
        vm_name = 'test2rest'

        data = self.assert_rest('/machines/by-name/?depth=1&attrs=hostname', method='get', auth=('a', 'a'))
        logging.debug("Machines by name: %s" % data)
        self.assert_rest('/machines/by-name/%s/vms' % data['children'][0]['hostname'],
                         method='post',
                         data=json.dumps({'hostname': vm_name,
                                          'template': config.oms_template,
                                          'start_on_boot': False,
                                          'root_password': 'a',
                                          'root_password_repeat': 'a'}),
                         auth=self.auth)
        self.assert_no_vm_rest(vm_name, auth=('b', 'b'))

    @unittest.skip('TODO: Move visibility tests to a separate suite')
    def test_user_hangar_vm_visibility(self):
        vm_name = 'test3rest'

        # Admin can create new backend
        self.assert_rest('/machines/hangar', method='post',
                         data=json.dumps({'backend': 'openvz'}),
                         auth=self.auth)
        self.assert_path('/machines/hangar', 'vms-openvz')

        # Unprivileged user can view backend
        self.assert_rest('/machines/hangar/vms-openvz', method='get', auth=('a', 'a'))

        # Admin can create new machines
        self.assert_rest('/machines/hangar/vms-openvz', method='post',
                         data=json.dumps({'hostname': vm_name,
                                          'template': config.oms_template,
                                          'root_password': 'opennode',
                                          'root_password_repeat': 'opennode',
                                          'start_on_boot': 'false'}), auth=self.auth)

        # Unprivileged user cannot view machines created by admin
        self.assert_no_hangar_compute_rest(vm_name, auth=('a', 'a'))
