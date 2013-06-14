import requests
import json
import time

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin


class ActionsHttpRestTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    def tearDown(self):
        pass

    def get_template(self, auth=None):
        r = requests.get('http://%s:8080/templates/by-name/?depth=1&attrs=name' % (self.host),
                         auth=auth)
        r.raise_for_status()
        data = r.json()
        return data[u'children'][0][u'name']

    def assert_vm_uuid_rest(self, compute, auth=None):
        r = requests.get('http://%s:8080/computes/?depth=1&attrs=id' % (self.host),
                         auth=(auth or getattr(self, 'auth')))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(True, unicode(compute) in map(lambda x: x['id'], data['children']))
        return data

    def test_createvm(self):
        self.template_name = self.get_template(self.auth)
        hostnamebase = 'test%s'
        hostcount = 101

        self.assert_rest('/machines/hangar/vms-openvz', method='get')
        while True:
            data = self.assert_rest('/machines/hangar/vms-openvz', method='post',
                                    data=json.dumps({'hostname': hostnamebase % hostcount,
                                                     'template': self.template_name,
                                                     'root_password': 'opennode',
                                                     'root_password_repeat': 'opennode',
                                                     'start_on_boot': 'false'}))

            uuid = data[u'result'][u'id']
            testurl = data[u'result']['url']

            for i in range(20):
                try:
                    self.assert_vm_uuid_rest(uuid)
                except Exception:
                    print 'Attempt failed:', i, uuid

            self.assert_vm_uuid_rest(uuid)
            for i in range(10):
                try:
                    self.assert_rest(testurl, method='delete')
                except requests.models.HTTPError:
                    print 'Delete attempt failed:', i, uuid
                    time.sleep(1)
                else:
                    break

            hostcount += 1
