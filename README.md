opennode-integration
====================

OpenNode integration test suite

**WARNING**: Integration tests are run against a local OMS server. Most of the data (including VMs) on that
server will be deleted befre and after tests running. For simplicity, test suites do not discriminate between
items created before and during tests. Make sure you're running the tests against a server specifically made
for the purpose of integration testing, not production server, or you risk losing all your data, including
all of your VMs!
