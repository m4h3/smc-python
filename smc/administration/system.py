"""
Module that controls aspects of the System itself, such as updating dynamic packages,
updating engines, applying global blacklists, etc.

To load the configuration for system, do::

    from smc.administration.system import System
    system = System()
    print system.smc_version
    print system.last_activated_package
    for pkg in system.update_package():
        print pkg

"""
import smc.actions.search as search
from smc.elements.other import prepare_blacklist
from .tasks import task_handler, Task
from smc.base.model import Meta, prepared_request, SubElement
from smc.administration.updates import EngineUpgrade, UpdatePackage
from smc.administration.license import License
from smc.api.common import fetch_json_by_post
from smc.api.exceptions import ActionCommandFailed
    
class System(SubElement):
    """
    System level operations such as SMC version, time, update packages, 
    and updating engines
    
    :ivar smc_version: version of SMC
    :ivar smc_time: SMC time
    :ivar last_activated_package: latest update package installed
    """
    def __init__(self, meta=None):
        meta = Meta(href=search.element_entry_point('system'))
        super(System, self).__init__(meta)
        pass
        
    @property    
    def smc_version(self):
        """
        Return the SMC version
        """
        return self._get_resource_by_link('smc_version').get('value')
    
    @property
    def smc_time(self):
        """
        Return the SMC time
        """
        return self._get_resource_by_link('smc_time').get('value')
    
    @property
    def last_activated_package(self):
        """
        Return the last activated package by id
        """
        return self._get_resource_by_link('last_activated_package').get('value')
    
    def empty_trash_bin(self):
        """ 
        Empty system level trash bin
        
        :raises: :py:class:`smc.api.exceptions.ActionCommandFailed`
        :return: None
        """
        prepared_request(ActionCommandFailed,
                         href=self._link('empty_trash_bin')).delete()

    def update_package(self):
        """
        Show all update packages on SMC 
        
        :return: list :py:class:`smc.administration.updates.UpdatePackage`
        """
        return [UpdatePackage(meta=Meta(**update))
                for update in self._get_resource_by_link('update_package')]
       
    def update_package_import(self):
        pass
        
    def engine_upgrade(self, engine_version=None):
        """
        List all engine upgrade packages available 
        
        Call this function without parameters to see available engine
        versions. Once you have found the engine version to upgrade, use
        the engine_version=href to obtain the guid. Obtain the download
        link and POST to download using 
        engine_upgrade_download(download_link) to download the update.
        
        :param engine_version: Version of engine to retrieve
        :return: dict of settings
        """
        return [EngineUpgrade(meta=Meta(**upgrade))
                for upgrade in self._get_resource_by_link('engine_upgrade')]
    
    def uncommitted(self):
        pass
    
    def system_properties(self):
        """
        List of all properties applied to the SMC
        """
        return self._get_resource_by_link('system_properties')
        
    def clean_invalid_filters(self):
        pass
    
    def blacklist(self, src, dst, duration=3600):
        """ 
        Add blacklist to all defined engines.
        Use the cidr netmask at the end of src and dst, such as:
        1.1.1.1/32, etc.
        
        :param src: source of the entry
        :param dst: destination of blacklist entry
        :raises: :py:class:`smc.api.exceptions.ActionCommandFailed`
        :return: None
        """
        prepared_request(ActionCommandFailed,
                         href=self._link('blacklist'),
                         json=prepare_blacklist(src, dst, duration)
                         ).create()

    @property
    def licenses(self):
        """
        List of all engine related licenses
        This will provide details related to whether the license is bound,
        granted date, expiration date, etc.
        ::
        
            for license in system.licenses:
                print(license, license.expiration_date)
                .....
        
        :return: list :py:class:`smc.administration.license.License`
        """
        licenses = self._get_resource_by_link('licenses')
        return [License(**lic)
                for lic in licenses['license']]
      
    def license_fetch(self):
        """
        Fetch available licenses for this SMC
        """
        return self._get_resource_by_link('license_fetch')
        
    def license_install(self):
        raise NotImplementedError
        
    def license_details(self):
        """
        This represents the license details for the SMC. This will include information
        with regards to the POL/POS, features, type, etc
        
        :return: dictionary of key/values
        """
        return self._get_resource_by_link('license_details')
        
    def license_check_for_new(self):
        """
        Check for new SMC license
        """
        return self._get_resource_by_link('license_check_for_new')
        
    def delete_license(self):
        raise NotImplementedError
    
    def visible_virtual_engine_mapping(self):
        """ 
        Mappings for master engines and virtual engines 
        
        :return: list of dict items related to master engines and virtual engine mappings
        """
        return self._get_resource_by_link('visible_virtual_engine_mapping')
    
    def references_by_element(self, element_href):
        """
        Return all references to element specified.
        
        :param str element_href: element reference
        :return: list list of references where element is used
        """
        result = fetch_json_by_post(href=self._link('references_by_element'),
                                    json={'value': element_href})
        if result.json:
            return result.json
        else:
            return []
    
    def export_elements(self, filename='export_elements.zip', typeof='all',
                        wait_for_finish=False):
        """
        Export elements from SMC.
        
        Valid types are: 
        all (All Elements)|nw (Network Elements)|ips (IPS Elements)|
        sv (Services)|rb (Security Policies)|al (Alerts)|
        vpn (VPN Elements)
        
        :param type: type of element
        :param filename: Name of file for export
        :raises: :py:class:`smc.api.exceptions.TaskRunFailed`
        :return: generator with results (if wait_for_finish=True), else href
        """
        valid_types = ['all', 'nw', 'ips', 'sv', 'rb', 'al', 'vpn']
        if not typeof in valid_types:
            typeof = 'all'
    
        element = prepared_request(href=self._link('export_elements'),
                                   params={'recursive': True,
                                           'type': typeof}
                                   ).create()
    
        return task_handler(Task(**element.json), 
                            wait_for_finish=wait_for_finish, 
                            filename=filename)
    
    def import_elements(self):
        raise NotImplementedError
    
    def unlicensed_components(self):
        raise NotImplementedError

    def snapshot(self):
        raise NotImplementedError
