import json
import logging
import requests
import time

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

log = logging.getLogger(__name__)

class ActionsHttpRestTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    # Overload NOT to call self.cleanup()
    def tearDown(self):
        pass

    def get_template(self, auth=None):
        r = requests.get('http://%s/templates/by-name/?depth=1&attrs=name' % (self.host),
                         auth=auth)
        r.raise_for_status()
        data = r.json()
        return data[u'children'][0][u'name']

    def assert_vm_uuid_rest(self, compute, auth=None):
        r = requests.get('http://%s/computes/?depth=1&attrs=id' % (self.host),
                         auth=(auth or getattr(self, 'auth')))
        r.raise_for_status()
        data = r.json()
        self.assertEqual(True, unicode(compute) in map(lambda x: x['id'], data['children']))
        return data

    def test_createvm(self):
        self.template_name = self.get_template(self.auth)
        hostnamebase = 'test%04d'
        hostcount = 1

        self.assert_rest('/machines/hangar/vms-openvz', method='get')
        while True:
            data = self.assert_rest('/machines/hangar/vms-openvz', method='post',
                                    data=json.dumps({'hostname': hostnamebase % hostcount,
                                                     'template': self.template_name,
                                                     'root_password': 'opennode',
                                                     'root_password_repeat': 'opennode',
                                                     'start_on_boot': 'false'}))

            uuid = data['result']['id']
            testurl = data['result']['url']

            result_array = []

            for i in range(20):
                try:
                    self.assert_vm_uuid_rest(uuid)
                    result_array.append(True)
                except Exception:
                    result_array.append(False)
                    time.sleep(0.1)

            previous = None
            count = 0
            for i in result_array:
                if i is not previous:
                    count += 1
                previous = i

            for i in range(10):
                try:
                    self.assert_rest(testurl, method='delete')
                except requests.models.HTTPError:
                    log.warning('Delete attempt failed: %s %s %s', i, uuid, hostnamebase % hostcount)
                    time.sleep(0.1)
                else:
                    break

            assert count < 3, 'More than 2 transitions: (%s) %s (%s)\n%s' % (count, uuid,
                                                                             hostnamebase % hostcount,
                                                                             result_array)
            hostcount += 1
