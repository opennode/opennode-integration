#!/bin/sh -ex
#
# Sets up test environment.

OMS_HOSTNAME="oms.test"
OMS_IP="192.168.1.85"
CTID="842"

# Create OMS instance
# FIXME ctid param not working
# FIXME start_vm param not working
# FIXME opennode CLI could support this (TUI-128)
salt-call --local onode.vm_deploy_vm "openvz:///system" \
	ctid="$CTID" \
	hostname="$OMS_HOSTNAME" \
	ip_address="$OMS_IP" \
	memory="2.0" \
	nameservers='"[]"' \
	start_vm=True \
	template_name="opennode-oms" \
	uuid="$(uuidgen)" \
	vm_type="openvz"
CTID=$(vzlist --all --hostname="$OMS_HOSTNAME" --no-header --output="ctid" | tr -d " ")
vzctl start "$CTID"

# Configure OMS
vzctl exec "$CTID" "/opt/oms/update.sh"
cp "/root/jenkins-id_rsa.pub" "/vz/private/$CTID/etc/opennode/authorized_keys"
sed -i 's/\[auth\]/\[auth\]\nuse_inmemory_pkcheck = True/' "/vz/private/$CTID/etc/opennode/opennode-oms.conf"
vzctl exec "$CTID" "/opt/oms/update.sh"
vzctl exec "$CTID" "systemctl restart oms"

# TODO: download/import template for testing

# Clear Salt minion cache
rm -f /etc/salt/pki/minion/minion*
vzctl exec "$CTID" salt-key --list-all
vzctl exec "$CTID" salt-key --delete-all --yes

# Register HN in OMS
opennode --register --oms-hostname "$OMS_IP"
vzctl exec "$CTID" salt-key --accept-all
vzctl exec "$CTID" salt-key --list-all

echo "All done."
