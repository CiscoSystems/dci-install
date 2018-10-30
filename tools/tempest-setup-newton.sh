#!/bin/bash

set -eux

### --start_docs

## Validate the overcloud deployment with tempest
## ==============================================

### --start_docs

## Configure tempest
## -----------------

## ::
source /home/stack/overcloudrc

## * Clean up from any previous tempest run
## ::

rm -rf /home/stack/tempest
# On doing tempest init workspace, it will create workspace directory
# as well as .workspace directory to store workspace information
# We need to delete .workspace directory otherwise tempest init failed
# to create tempest directory.
rm -rf /home/stack/.tempest
rm -rf /home/stack/tempest_git
rm -rf /home/stack/python-tempestconf

## * Clean up network if it exists from previous run
## ::

for i in $(neutron floatingip-list -c id -f value)
do
    neutron floatingip-disassociate $i
    neutron floatingip-delete $i
done
for i in $(neutron router-list -c id -f value); do neutron router-gateway-clear $i; done
for r in $(neutron router-list -c id -f value); do
    for p in $(neutron router-port-list $r -c id -f value); do
        neutron router-interface-delete $r port=$p || true
    done
done
for i in $(neutron router-list -c id -f value); do neutron router-delete $i; done
for i in $(neutron port-list -c id -f value); do neutron port-delete $i; done
for i in $(neutron net-list -c id -f value); do neutron net-delete $i; done

neutron net-create public --router:external=True \
    --provider:network_type vlan \
    --provider:segmentation_id 1261 \
    --provider:physical_network datacentre


public_net_id=$(neutron net-show public -f value -c id)

neutron subnet-create --name ext-subnet \
    --allocation-pool \
    start=20.0.0.10,end=20.0.0.200 \
    --disable-dhcp \
    --gateway 20.0.0.1 \
    public 20.0.0.0/24

## * Ensure creator and Member role is present
## * Member role is needed for Heat tests.
## * creator role is needed for Barbican for running volume encryption tests.
## ::
openstack role show Member > /dev/null || openstack role create Member

openstack role show creator > /dev/null || openstack role create creator

## * Generate a tempest configuration
## ::

mkdir /home/stack/tempest
# Install OpenStack Tempest, python-junitxml for Newton
# From Ocata, config_tempest is moved to python-tempestconf. So for
# Ocata onwards, Install python-tempestconf
sudo yum -y install openstack-tempest python-junitxml
# Create Tempest Workspace from tempest rdo package
cd /home/stack/tempest
/usr/share/openstack-tempest-*/tools/configure-tempest-directory

# Install OpenStack Services Tempest plugin
# FIXME(chkumar246): Install tempest plugin from package currently then switch to install_test_packages script
sudo yum -y install python-ceilometer-tests python-zaqar-tests python-ironic-inspector-tests \
    python-gnocchi-tests python-aodh-tests python-mistral-tests python-heat-tests python-keystone-tests \
    python-ironic-tests python-neutron-tests python-cinder-tests

# Generate tempest configuration files
export TEMPESTCONF="/home/stack/tempest/tools/config_tempest.py"

# Go to Tempest Workspace
cd /home/stack/tempest

# Generate Tempest Config file using python-tempestconf
# Notice aodh_plugin will be set to False if telemetry service is disabled
# TODO(arxcruz) In the future the
# compute_feature_enabled.attach_encrypted_volume should be handled by
# python-tempestconf tool
${TEMPESTCONF} --out etc/tempest.conf \
  --network-id $public_net_id \
  --deployer-input ~/tempest-deployer-input.conf \
  --image http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img \
  --debug \
      --remove network-feature-enabled.api_extensions=dvr \
      --create \
    identity.uri $OS_AUTH_URL \
  identity.admin_password $OS_PASSWORD \
  identity.admin_username $OS_USERNAME \
  compute.allow_tenant_isolation true \
  scenario.img_file cirros-0.3.5-x86_64-disk.img \
    compute-feature-enabled.attach_encrypted_volume False \
  network.tenant_network_cidr 192.168.0.0/24 \
  compute.build_timeout 500 \
  volume-feature-enabled.api_v1 False \
  validation.image_ssh_user cirros \
  validation.ssh_user cirros \
  network.build_timeout 500 \
  volume.build_timeout 500 \
        heat_plugin.instance_type m1.micro \
    volume-feature-enabled.backup False \
    heat_plugin.admin_password $OS_PASSWORD \
    heat_plugin.minimal_instance_type m1.micro \
    service_available.novajoin False \
    service_available.designate False \
    service_available.ec2api False \
    service_available.ceilometer False \
    service_available.mistral False \
    heat_plugin.admin_username $OS_USERNAME \
    heat_plugin.tenant_name demo \
    service_available.barbican False \
    heat_plugin.username demo \
    heat_plugin.region regionOne \
    heat_plugin.minimal_image_ref cirros-0.3.5-x86_64-disk.img \
    heat_plugin.user_domain_name Default \
    heat_plugin.project_domain_name Default \
    service_available.kuryr False \
    heat_plugin.auth_url $OS_AUTH_URL \
    network.floating_network_name public \
    service_available.sahara False \
    heat_plugin.skip_functional_tests True \
    heat_plugin.password secrete \
    heat_plugin.image_ref cirros-0.3.5-x86_64-disk.img \
      compute-feature-enabled.console_output true \
  orchestration.stack_owner_role Member
  
### --stop_docs

### --start_docs

## Run tempest
## -----------

## ::

## FIXME(chkumar246): Tempest run interface is unstable till that use ostestr for
## running tests: https://bugs.launchpad.net/tempest/+bug/1669455

export OSTESTR='ostestr'
export TEMPESTCLI='/usr/bin/tempest'

## List tempest plugins
$TEMPESTCLI list-plugins

## Save the resources before running tempest tests
## It will create saved_state.json in tempest workspace.
$TEMPESTCLI cleanup --init-saved-state

$OSTESTR  --whitelist_file=/home/stack/whitelist_file.conf  --concurrency 6
## Check which all tenants would be modified in the tempest run
## It will create dry_run.json in tempest workspace.
$TEMPESTCLI cleanup --dry-run

### --stop_docs
### --stop_docs
