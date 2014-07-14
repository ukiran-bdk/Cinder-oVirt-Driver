# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
# Copyright 2011 OpenStack LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Driver for ovirt volumes.

"""

from oslo.config import cfg

import ovirtsdk.api
from ovirtsdk.xml import params
from ovirtsdk.xml.params import Disk, StorageDomains

from cinder import exception
from cinder.openstack.common import log as logging
from cinder.volume import driver
from cinder.volume import volume_types

LOG = logging.getLogger(__name__)
#LOG.debug("message")
#LOG.debug(_("************rhevm - spawn*************"))
#LOG.debug(_(" network_info--------->>>>  %s" %network_info))

ovirt_volume_opts = [
    cfg.StrOpt('ovirt_engine_url',
               default='https://10.10.22.32:443/api',
               help=''),
    cfg.StrOpt('ovirt_engine_username',
               default='admin@internal',
               help=''),
    cfg.StrOpt('ovirt_engine_password',
               default='iso*help',
               help=''),
    cfg.StrOpt('ovirt_engine_storagedomain',
               default='DataNFS',
               help=''),
    cfg.StrOpt('ovirt_engine_sparse',
               default=True,
               help=''),
]

CONF = cfg.CONF
CONF.register_opts(ovirt_volume_opts)

class oVirtVolumeDriver(driver.VolumeDriver):
    """Manage volumes on oVirt."""
    
    VERSION = '1.0'
    VOLSIZE_MULT = 2 ** 30  # Gigabytes to bytes
    
    def __init__(self, *args, **kwargs):
        LOG.info(_("************CVD - __init__*************"))
        #self._engine = ovirtsdk.api.API(url="https://10.10.22.32:443/api",username="admin@internal",password="iso*help",insecure=True)
        self._engine = ovirtsdk.api.API(url=CONF.ovirt_engine_url,username = CONF.ovirt_engine_username, password = CONF.ovirt_engine_password,insecure=True)
        #self._initialized
        
        
    def do_setup(self, context):
        LOG.info(_("************CVD - do_setup_*************"))
        """Any initialization the volume driver does while starting"""
        #self._engine = ovirtsdk.api.API(CONF.ovirt_engine_url,CONF.ovirt_engine_username, CONF.ovirt_engine_password)
        #self._engine = ovirtsdk.api.API(url="https://10.10.22.32:443/api",username="admin@internal",password="iso*help",insecure=True)
        self._engine = ovirtsdk.api.API(url=CONF.ovirt_engine_url,username = CONF.ovirt_engine_username, password = CONF.ovirt_engine_password,insecure=True)

    def check_for_setup_error(self):
        LOG.info(_("************CVD - check_for_setup_error*************"))
        """No setup necessary in fake mode."""
        pass
    
    def initialize_connection(self, volume, connector):
        LOG.info(_("************CVD - initialize_connection*************"))
        """Allow connection to connector and return connection info."""
        LOG.info(_("*******rhevm - initialize_connection - volume---->>%s" %volume))
        LOG.info(_("*******rhevm - initialize_connection - volume[name]---->>%s" %volume['name']))
        LOG.info(_("*******rhevm - initialize_connection - volume[display_name]---->>%s" %volume['display_name']))
        return {
        'driver_volume_type': 'ovirt',
        'data' : {'volume': 123,'volume_id': volume['id'], 'volume_name':volume['display_name']}
        #name='DiskFromCVD'+ volume['name']
        }
        
        #raise NotImplementedError()

    def terminate_connection(self, volume, connector, **kwargs):
        LOG.info(_("************CVD - terminate_connection*************"))
        LOG.info(_("*******rhevm - terminate_connection - volume---->>%s" %volume))
        LOG.info(_("*******rhevm - terminate_connection - volume[name]---->>%s" %volume['name']))
        LOG.info(_("*******rhevm - terminate_connection - volume[display_name]---->>%s" %volume['display_name']))
        """Disallow connection from connector"""
        pass
        #raise NotImplementedError()
    
    def create_volume(self, volume):
        LOG.info(_("************CVD - create_volume*************"))
        #domain = api.storagedomains.get(name='DataNFS') 
        #LOG.info(_("************CVD -  volume['name'] *************--->>%s"%volume['name']))
        domain = self._engine.storagedomains.get(CONF.ovirt_engine_storagedomain)
        storageDomain = params.StorageDomains(storage_domain=[domain])
        #volume_size = volume['size']
        size = volume['size'] * pow(2, 30) 
        diskType = 'data' 
        diskFormat = 'cow' 
        diskInterface = 'virtio' 
        sparse = True 
        bootable = False
        #vol_name = 'DiskFromCVD'+ volume['name']
        vol_name = volume['display_name']
        request = Disk(
                       name=vol_name,
                       storage_domains=storageDomain,
                       size=size, 
                       type_=diskType,
                       interface=diskInterface, 
                       format=diskFormat, 
                       #sparse=FLAGS.ovirt_engine_sparse,
                       sparse=sparse,
                       bootable=bootable)
        response = self._engine.disks.add(request)
        LOG.info(_("************CVD - create_volume successful*************"))
    
    def delete_volume(self, volume):
        LOG.info(_("************CVD - delete_volume*************"))
        #vol_name = 'DiskFromCVD'+ volume['name']
        vol_name = volume['display_name']
        
        LOG.info(_("************CVD - delete *************--->>%s"%vol_name))
        for disk in self._engine.disks.list(name=vol_name):
            disk.delete()
        return True
    
    def extend_volume(self, volume, new_size):
        LOG.info(_("************CVD - extend_volume*************"))
        pass
        
    def create_snapshot(self, snapshot):
        LOG.info(_("************CVD - create_snapshot*************"))
        pass
    
    def create_volume_from_snapshot(self, volume, snapshot):
        LOG.info(_("************CVD - create_volume_from_snapshot*************"))
        pass
    
    def delete_snapshot(self, snapshot):
        LOG.info(_("************CVD - delete_snapshot*************"))
        pass
    
    def ensure_export(self, context, volume):
        LOG.info(_("************CVD - ensure_export*************"))
        """Synchronously recreates an export for a logical volume."""
        # raise NotImplementedError()
        pass
    
    def create_export(self, context, volume):
        LOG.info(_("************CVD - create_export*************"))
        """Exports the volume. Can optionally return a Dictionary of changes
        to the volume object to be persisted."""
        # raise NotImplementedError()
        pass
    
    def remove_export(self, context, volume):
        LOG.info(_("************CVD - remove_export*************"))
        """Removes an export for a logical volume."""
        # raise NotImplementedError()
        pass    
    
    def copy_image_to_volume(self, context, volume, image_service, image_id):
        LOG.info(_("************CVD - copy_image_to_volume*************"))
        pass
    
    def copy_volume_to_image(self, context, volume, image_service, image_meta):
        LOG.info(_("************CVD - copy_volume_to_image*************"))
        pass
    
    def create_cloned_volume(self, volume, src_vref):
        LOG.info(_("************CVD - create_cloned_volume*************"))
        pass
    
    def get_volume_stats(self, refresh=False):
        #LOG.debug(_("************CVD - get_volume_stats*************"))
        LOG.info(_("************CVD - get_volume_stats*************"))
        """Get volume stats.

        If 'refresh' is True, update the stats first.
        """
        if refresh or not self._stats:
            self._update_volume_stats()

        return self._stats
        
    def _update_volume_stats(self):
        LOG.info(_("************CVD - _update_volume_stats*************"))
        """Retrieve stats info from volume group."""
        
        data = {}
        data['volume_backend_name'] = 'oVirt Storage'
        data['vendor_name'] = 'oVirt'
        data['driver_version'] = '1.0'
                
        storagedomain = self._engine.storagedomains.get(CONF.ovirt_engine_storagedomain)
        disk_used = storagedomain.get_used() / (1024 * 1024 * 1024)
        disk_available = storagedomain.get_available() / (1024 * 1024 * 1024)
        disk_total = disk_used + disk_available
        
        #print  storagedomain.storage.type_
        #print 'Type - ', storagedomain.type_
        #print 'Used - ', disk_used
        #print 'Available - ' , disk_available
        #print 'Total - ', disk_total
        
        data['storage_protocol'] = storagedomain.storage.type_
        data['total_capacity_gb'] = disk_total
        data['free_capacity_gb'] = disk_available
        data['reserved_percentage'] = 0
        data['QoS_support'] = False
        
        self._stats = data
    
    def backup_volume(self, context, backup, backup_service):
        LOG.info(_("************CVD - backup_volume*************"))
        pass
    
    def restore_backup(self, context, backup, volume, backup_service):
        LOG.info(_("************CVD - restore_backup*************"))
        pass
    
    def local_path(self, volume):
        LOG.info(_("************CVD - local_path*************"))
        pass
    
    def remote_path(self, volume):
        LOG.info(_("************CVD - remote_path*************"))
        pass
    
    
        
    
    