import json
import unittest

from integration_test_base import BaseIntegrationTest, IntegrationTestRestMixin

class HttpRestPathHandlingTestCase(BaseIntegrationTest, IntegrationTestRestMixin):

    def test_basic_auth_accessible(self):
        self.assert_rest('/basicauth?basic_auth=false&username=%s&password=%s' % self.auth, method='get')

    def test_auth_accessible_as_basic_auth(self):
        self.assert_rest('/auth?basic_auth=true', method='get', auth=self.auth)

    def test_auth_accessible_as_auth(self):
        self.assert_rest('/auth', method='post', data={'username': self.auth[0], 'password': self.auth[1]})
