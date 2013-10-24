#!/bin/sh -ex
#
# Sets up test environment.
#
# *** THI SCRIPT IS TO BE RUN MANUALLY ***

OMS_HOSTNAME="192.168.1.85"

# Create OMS instance
# FIXME: Need to automate this (TUI-128)
opennode

CTID=$(vzlist --hostname="oms.*" --no-header --output="ctid" | tr -d " ")

# Configure OMS
vzctl exec "$CTID" "/opt/oms/update.sh"
cp "/root/jenkins-id_rsa.pub" "/vz/private/$CTID/etc/opennode/authorized_keys"
sed -i 's/\[auth\]/\[auth\]\nuse_inmemory_pkcheck = True/' "/vz/private/$CTID/etc/opennode/opennode-oms.conf"
vzctl exec "$CTID" "/opt/oms/update.sh"
vzctl exec "$CTID" "systemctl restart oms"

# Clear Salt minion cache
rm -f /etc/salt/pki/minion/minion*
vzctl exec "$CTID" salt-key --list-all
vzctl exec "$CTID" salt-key --delete-all --yes

# Register HN in OMS
opennode --register --oms_hostname "$OMS_HOSTNAME"
vzctl exec "$CTID" salt-key --accept-all
vzctl exec "$CTID" salt-key --list-all

echo "All done."
