import requests

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin


class HttpRestPathHandlingTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    def test_basic_auth_accessible(self):
        self.assert_rest('/basicauth?basic_auth=false&username=%s&password=%s' % self.auth, method='get')

    def test_auth_accessible_as_basic_auth(self):
        self.assert_rest('/auth?basic_auth=true', method='get', auth=self.auth)

    def test_auth_accessible_as_auth(self):
        self.assert_rest('/auth', method='post', data={'username': self.auth[0], 'password': self.auth[1]})

    def test_cookie_based_auth(self):
        auth_request = requests.get('http://%s/auth' % self.host, auth=self.auth)
        self.assert_rest_request_succeeded(auth_request)
        token = auth_request.cookies['oms_auth_token']

        control_request = requests.get('http://%s/proc' % self.host, cookies={'oms_auth_token': token})
        self.assert_rest_request_succeeded(control_request)

    def test_header_based_auth(self):
        auth_request = requests.get('http://%s/auth' % self.host, auth=self.auth)
        self.assert_rest_request_succeeded(auth_request)
        token = auth_request.headers['x-oms-security-token']

        control_request = requests.get('http://%s/proc' % self.host, headers={'x-oms-security-token': token})
        self.assert_rest_request_succeeded(control_request)

    def test_request_param_based_auth(self):
        auth_request = requests.get('http://%s/auth' % self.host, auth=self.auth)
        self.assert_rest_request_succeeded(auth_request)
        token = auth_request.json()['token']

        control_request = requests.get('http://%s/proc' % self.host, params={'security_token': token})
        self.assert_rest_request_succeeded(control_request)

    def test_basic_auth_yields_a_single_token(self):
        r = self.assert_rest('/auth?basic_auth=true', auth=self.auth)
        # r = requests.get('http://%s/auth' % self.host, auth=self.auth)

        header_tokens = r.headers['x-oms-security-token'].split(',')
        self.assertEqual(1, len(header_tokens), 'A single security token header expected')

        # Set-Cookie headers must be parsed manually here since requests merges them
        cookie_tokens = [h for h in r.headers['set-cookie'].split(',') if h.startswith('oms_auth_token')]
        self.assertEqual(1, len(cookie_tokens), 'A single security cookie expected')
