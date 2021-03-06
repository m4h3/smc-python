import smc.actions.search as search
from smc.compat import min_smc_version
from smc.elements.helpers import domain_helper
from smc.base.model import Meta, Element, prepared_request, ResourceNotFound,\
    SubElement
from smc.api.exceptions import LoadEngineFailed, UnsupportedEngineFeature,\
    UnsupportedInterfaceType, TaskRunFailed, EngineCommandFailed,\
    SMCConnectionError, CertificateError, CreateElementFailed
from smc.core.node import Node
from smc.core.resource import Snapshot
from smc.core.interfaces import PhysicalInterface, \
    VirtualPhysicalInterface, TunnelInterface, Interface
from smc.administration.tasks import task_handler, Task
from smc.elements.other import prepare_blacklist
from smc.elements.network import Alias
from smc.vpn.elements import VPNSite
from smc.core.route import Antispoofing, Routing, Routes

class Engine(Element):
    """
    Instance attributes:
    
    :ivar name: name of engine
    :ivar type: type of engine
    :ivar dict json: raw engine json
    :ivar href: href of the engine
    :ivar etag: current etag
    :ivar link: list link to engine resources
    
    Instance resources:
    
    :ivar list nodes: :py:class:`smc.core.node.Node` nodes associated with 
          this engine
    :ivar permissions: :py:class:`smc.administration.access_rights.AccessControlList`
    :ivar routing: :py:class:`smc.core.route.Routing` routing configuration hierarchy
    :ivar routing_monitoring: :py:class:`smc.core.route.Routes` current route table
    :ivar antispoofing: :py:class:`smc.core.route.Antispoofing` antispoofing interface
          configuration
    :ivar interface: :py:class:`smc.core.interfaces.Interface` interfaces 
          for this engine
    :ivar internal_gateway: :py:class:`~InternalGateway` engine 
          level VPN settings
    :ivar virtual_resource: :py:class:`smc.core.engine.VirtualResource` for engine, 
          only relavant to Master Engine
    :ivar physical_interface: :py:class:`smc.core.interfaces.PhysicalInterface` 
          access to physical interface settings
    :ivar tunnel_interface: :py:class:`smc.core.interfaces.TunnelInterface` 
          retrieve or create tunnel interfaces
    :ivar snapshots: :py:class:`smc.core.engine.Snapshot` engine level policy snapshots

    """
    def __init__(self, name, meta=None, **kwargs):
        super(Engine, self).__init__(name, meta)
        pass
        
    @classmethod
    def create(cls, name, node_type, 
               physical_interfaces,
               nodes=1, log_server_ref=None, 
               domain_server_address=None,
               enable_antivirus=False, enable_gti=False,
               default_nat=False, location_ref=None,
               enable_ospf=None, ospf_profile=None):
        """
        Create will return the engine configuration as a dict that is a 
        representation of the engine. The creating class will also add 
        engine specific requirements before constructing the request
        and sending to SMC (which will serialize the dict to json).
        
        :param name: name of engine
        :param str node_type: comes from class attribute of engine type
        :param dict physical_interfaces: physical interface list of dict
        :param int nodes: number of nodes for engine
        :param str log_server_ref: href of log server
        :param list domain_server_address: dns addresses
        """
        node_list = []
        for nodeid in range(1, nodes+1): #start at nodeid=1
            node_list.append(Node.create(name, node_type, nodeid))
            
        domain_server_list = []
        if domain_server_address:
            rank_i = 0
            for entry in domain_server_address:
                domain_server_list.append(
                                    {"rank": rank_i, "value": entry})
        
        #Set log server reference, if not explicitly provided
        if not log_server_ref and node_type is not 'virtual_fw_node': 
            log_server_ref = search.get_first_log_server()
            
        base_cfg = {'name': name,
                    'nodes': node_list,
                    'domain_server_address': domain_server_list,
                    'log_server_ref': log_server_ref,
                    'physicalInterfaces': physical_interfaces}
        if enable_antivirus:
            antivirus = {'antivirus': {
                            'antivirus_enabled': True,
                            'antivirus_update': 'daily',
                            'virus_log_level': 'stored',
                            'virus_mirror': 'update.nai.com/Products/CommonUpdater'}}
            base_cfg.update(antivirus)
        if enable_gti:
            gti = {'gti_settings': {
                        'file_reputation_context': 'gti_cloud_only'}}
            base_cfg.update(gti)
        if default_nat:
            nat = {'default_nat': True}
            base_cfg.update(nat)
        if location_ref:
            location = {'location_ref': location_ref}
            base_cfg.update(location)
        if enable_ospf:
            if not ospf_profile: #get default profile
                ospf_profile = search.get_ospf_default_profile()
            ospf = {'dynamic_routing': {
                        'ospfv2': {
                            'enabled': True,
                            'ospfv2_profile_ref': ospf_profile}}}
            base_cfg.update(ospf)
        
        return base_cfg
          
    def load(self):
        """ 
        When engine is loaded, save the attributes that are needed. 
        Engine load can be called directly::
        
            engine = Engine('myengine').load()
            
        or load by calling collection.describe_xxx methods::
        
            for fw in describe_single_fws():
                if fw.name == 'myfw':
                    engine = fw.load()
                    
        Call this to reload settings, useful if changes are made and new 
        configuration references or updated attributes are needed.
        """
        try:
            if not self.meta:
                if not min_smc_version(6.1):
                    result = search.element_info_as_json(self.name)
                    if result and len(result) == 1:
                        self.meta = Meta(**result[0])
                        result = search.element_by_href_as_json(self.href)
                        if not result.get('nodes'):
                            raise LoadEngineFailed('Cannot load engine name: {}, please ensure the name ' 
                                                   'is correct. An element was returned but was of type: '
                                                   '{}'.format(self._name, self.meta.type))
                    else: #error
                        if result:
                            names = [name.get('name') for name in result 
                                     if name.get('name')]
                        else:
                            names = []
                        raise LoadEngineFailed('Cannot load engine name: {}, ensure the '
                                               'name is correct and that the engine exists. '
                                               'Search returned: {}'
                                               .format(self._name, names))
            self.cache()
            return self    

        except LoadEngineFailed:
            raise

    @property
    def version(self):
        """
        Version of this engine
        """
        return self.attr_by_name('engine_version')
        
    @property
    def type(self):
        """
        Engine type
        """
        if not self.meta: self.load()    
        return self.meta.type
    
    def rename(self, name):
        """
        Rename the firewall engine, nodes, and internal gateway (vpn)

        :return: None
        """
        self.modify_attribute(name='{}'.format(name))
        self.internal_gateway.modify_attribute(name='{} Primary'\
                                               .format(name))
        for node in self.nodes:
            node.modify_attribute(name='{} node {}'.format(name, node.nodeid))
        self._name = self.data.get('name')
        
    @property
    def nodes(self):
        """
        Return a list of child nodes of this engine. This can be
        used to iterate to obtain access to node level operations
        
        :return: list :py:class:`smc.core.node.Node`
        """
        return [Node(meta=Meta(**node))
                for node in self._get_resource_by_link('nodes')]

    @property
    def permissions(self):
        """
        Retrieve the permissions for this engine instance.
        ::
        
            for acl in engine.permissions:
                print(acl, acl.granted_element)
        
        :return: list :py:class:`smc.administration.access_rights.AccessControlList`
        """
        try:
            acls = self._get_resource_by_link('permissions')
            return [Element.from_href(acl) 
                    for acl in acls['granted_access_control_list']]
    
        except ResourceNotFound:
            raise UnsupportedEngineFeature('Engine permissions are only supported '
                                           'when using SMC API version 6.1 and newer.')
    
    def alias_resolving(self):
        """ 
        Alias definitions with resolved values as defined on this engine. 
        Aliases can be used in rules to simplify multiple object creation
        ::
        
            print(list(engine.alias_resolving()))
        
        :return: generator :py:class:`smc.elements.network.Alias`
        """
        for alias in self._get_resource_by_link('alias_resolving'):
            yield Alias.load(alias)
  
    def blacklist(self, src, dst, duration=3600):
        """ 
        Add blacklist entry to engine node by name. For blacklist to work,
        you must also create a rule with action "Apply Blacklist".
    
        :param str src: source to blacklist, can be /32 or network cidr
        :param str dst: dest to deny to, 0.0.0.0/32 indicates all destinations
        :param int duration: how long to blacklist in seconds
        :raises: :py:class:`smc.api.exceptions.EngineCommandFailed`
        :return: None
        """
        prepared_request(EngineCommandFailed,
                         href=self._link('blacklist'),
                         json=prepare_blacklist(src, dst, duration)
                         ).create()

    def blacklist_flush(self):
        """ 
        Flush entire blacklist for engine
    
        :raises: :py:class:`smc.api.exceptions.EngineCommandFailed`
        :return: None
        """
        prepared_request(EngineCommandFailed,
                         href=self._link('flush_blacklist')
                         ).delete()
    
    def add_route(self, gateway, network):
        """ 
        Add a route to engine. Specify gateway and network. 
        If this is the default gateway, use a network address of
        0.0.0.0/0.
        
        .. note: This will fail if the gateway provided does not have a 
                 corresponding interface on the network.
        
        :param str gateway: gateway of an existing interface
        :param str network: network address in cidr format
        :raises: `smc.api.exceptions.EngineCommandFailed`
        :return: None
        """
        prepared_request(EngineCommandFailed,
                         href=self._link('add_route'),
                         params={'gateway': gateway, 
                                 'network': network}
                         ).create()

    @property                            
    def routing(self):
        """
        Find all routing nodes within engine::
    
            for routing_node in engine.routing.all():
                for routes in routing_node:
                    print(routes)

        :return: :py:class:`smc.core.route.Routing`
        """
        href = self._link('routing')
        return Routing(meta=Meta(href=href),
                       data=self._get_resource(href))
    
    @property
    def routing_monitoring(self):
        """ 
        Return route table for the engine, including 
        gateway, networks and type of route (dynamic, static). 
        Calling this can take a few seconds to retrieve routes
        from the engine.
        
        Find all routes for engine resource::
            
            engine = Engine('myengine')
            for route in engine.routing_monitoring.all():
                print route
      
        :raises: `smc.api.exceptions.EngineCommandFailed`: routes cannot be retrieved
        :return: list :py:class:`smc.core.route.Routes`
        """
        try:
            result = prepared_request(EngineCommandFailed,
                                      href=self._link('routing_monitoring')
                                      ).read()
            return Routes(result.json)
        except SMCConnectionError:
            raise EngineCommandFailed('Timed out waiting for routes')
    
    @property                     
    def antispoofing(self):
        """ 
        Antispoofing interface information. By default is based on routing
        but can be modified.
        ::
            
            for entry in engine.antispoofing.all():
                print(entry)
        
        :return: :py:class:`smc.core.route.Antispoofing`
        """
        href = self._link('antispoofing')
        return Antispoofing(meta=Meta(href=href),
                            data=self._get_resource(href))
    @property
    def internal_gateway(self):
        """ 
        Engine level VPN gateway information. This is a link from
        the engine to VPN level settings like VPN Client, Enabling/disabling
        an interface, adding VPN sites, etc. 

        :raises: :py:class:`smc.api.exceptions.UnsupportedEngineFeature`
        :return: :py:class:`~InternalGateway`
        """
        try:
            result = self._get_resource_by_link('internal_gateway')
            if result:
                return InternalGateway(meta=Meta(**result.pop()))
        except ResourceNotFound:
            raise UnsupportedEngineFeature('This engine does not support an internal '
                                           'gateway for VPN, engine type: {}'\
                                           .format(self.type))
   
    @property
    def virtual_resource(self):
        """ Master Engine only 
        
        To get all virtual resources call::
            
            engine.virtual_resource.all()
            
        :raises: :py:class:`smc.api.exceptions.UnsupportedInterfaceType`
        :return: :py:class:`smc.elements.engine.VirtualResource`
        """
        try:
            return VirtualResource(meta=Meta(href=self._link('virtual_resources')))
        except ResourceNotFound:
            raise UnsupportedEngineFeature('This engine does not support virtual '
                                           'resources; engine type: {}'\
                                          .format(self.type))

    @property    
    def interface(self):
        """ 
        Get all interfaces, including non-physical interfaces such
        as tunnel or capture interfaces. These are returned as Interface 
        objects and can be used to load specific interfaces to modify, etc.
        ::
        
            for interfaces in engine.interface.all():
                ......
        
        :return: :py:class:`smc.core.interfaces.Interface`
        
        See :py:class:`smc.core.interfaces.Interface` for more info
        """
        return Interface(meta=Meta(href=self._link('interfaces')), 
                         engine=self)
    
    @property
    def physical_interface(self):
        """ 
        Returns a PhysicalInterface. This property can be used to
        add physical interfaces to the engine. For example::
        
            engine.physical_interface.add_single_node_interface(....)
            engine.physical_interface.add_node_interface(....)

        :raises: :py:class:`smc.api.exceptions.UnsupportedInterfaceType`
        :return: :py:class:`smc.core.interfaces.PhysicalInterface`
        """
        try:
            return PhysicalInterface(meta=Meta(href=self._link('physical_interface')), 
                                     engine=self)
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Engine type: {} does not support the '
                                           'physical interface type'\
                                           .format(self.type))
    @property    
    def virtual_physical_interface(self):
        """ Master Engine virtual instance only
        
        A virtual physical interface is for a master engine virtual instance. This
        interface type is just a subset of a normal physical interface but for virtual
        engines. This interface only sets Auth_Request and Outgoing on the interface.
        
        To view all interfaces for a virtual engine::
        
            for intf in engine.virtual_physical_interface.all():
                print intf.describe()
        
        :raises: :py:class:`smc.api.exceptions.UnsupportedInterfaceType`
        :return: :py:class:`smc.core.interfaces.VirtualPhysicalInterface`
        """
        try:
            return VirtualPhysicalInterface(meta=Meta(href=self._link('virtual_physical_interface')), 
                                            engine=self)
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Only virtual engines support the '
                                           'virtual physical interface type. Engine '
                                           'type is: {}'
                                           .format(self.type))

    @property
    def tunnel_interface(self):
        """ 
        Get only tunnel interfaces for this engine node.
        
        :raises: :py:class:`smc.api.exceptions.UnsupportedInterfaceType`
        :return: :py:class:`smc.core.interfaces.TunnelInterface`
        """
        try:
            return TunnelInterface(meta=Meta(href=self._link('tunnel_interface')), 
                                   engine=self)
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Tunnel interfaces are only supported on '
                                           'layer 3 single engines or clusters; '
                                           'Engine type is: {}'
                                           .format(self.type))

    @property
    def modem_interface(self):
        """ 
        Get only modem interfaces for this engine node.
        
        :return: list of dict entries with href,name,type, or None
        """
        try:
            return self._get_resource_by_link('modem_interface')
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Modem interfaces are not supported '
                                           'on this engine type: {}'
                                           .format(self.type))
    
    @property
    def adsl_interface(self):
        """ 
        Get only adsl interfaces for this engine node.
        
        :return: list of dict entries with href,name,type, or None
        """
        try:
            return self._get_resource_by_link('adsl_interface')
        except ResourceNotFound:
            raise UnsupportedInterfaceType('ADSL interfaces are not supported '
                                           'on this engine type: {}'
                                           .format(self.type))
    
    @property
    def wireless_interface(self):
        """ 
        Get only wireless interfaces for this engine node.

        :return: list of dict entries with href,name,type, or None
        """
        try:
            return self._get_resource_by_link('wireless_interface')
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Wireless interfaces are not supported '
                                           'on this engine type: {}'
                                           .format(self.type))
    
    @property
    def switch_physical_interface(self):
        """ 
        Get only switch physical interfaces for this engine node.

        :return: list of dict entries with href,name,type, or None
        """
        try:
            return self._get_resource_by_link('switch_physical_interface')
        except ResourceNotFound:
            raise UnsupportedInterfaceType('Switch interfaces are not supported '
                                           'on this engine type: {}'
                                           .format(self.type))
    
    def refresh(self, wait_for_finish=True, sleep=3):
        """ 
        Refresh existing policy on specified device. This is an asynchronous 
        call that will return a 'follower' link that can be queried to determine 
        the status of the task. 
        
        Last yield is result href; if wait_for_finish=False, the only yield is 
        the follower href::
        
            task = engine.refresh()
            for message in task:
                print message

        :param boolean wait_for_finish: whether to wait in a loop until the upload completes
        :param int sleep: number of seconds to sleep if wait_for_finish=True
        :raises: :py:class:`smc.api.exceptions.TaskRunFailed`
        :return: generator yielding updates on progress
        """
        element = prepared_request(TaskRunFailed,
                                   href=self._link('refresh')
                                   ).create()
       
        return task_handler(Task(**element.json), 
                            wait_for_finish=wait_for_finish,
                            sleep=sleep)

    def upload(self, policy=None, wait_for_finish=False, sleep=3):
        """ 
        Upload policy to engine. This is used when a new policy is required
        for an engine, or this is the first time a policy is pushed to an engine.
        If an engine already has a policy and the intent is to re-push, then use
        :py:func:`refresh` instead.
        The policy argument can use a wildcard * to specify in the event a full 
        name is not known::
        
            engine = Engine('myfw')
            task = engine.upload('Amazon*', wait_for_finish=True)
            for message in task:
                print message
        
        :param str policy: name of policy to upload to engine; if None, current policy
        :param boolean wait_for_finish: whether to wait for async responses
        :param int sleep: number of seconds to sleep if wait_for_finish=True
        :raises: :py:class:`smc.api.exceptions.TaskRunFailed`
        :return: generator yielding updates on progress
        """
        element = prepared_request(TaskRunFailed,
                                   href=self._link('upload'),
                                   params={'filter': policy}).create()
        
        return task_handler(Task(**element.json), 
                            wait_for_finish=wait_for_finish,
                            sleep=sleep)

    def generate_snapshot(self, filename='snapshot.zip'):
        """ 
        Generate and retrieve a policy snapshot from the engine
        This is blocking as file is downloaded

        :param str filename: name of file to save file to, including directory path
        :raises: :py:class:`smc.api.exceptions.EngineCommandFailed`
        :return: None
        """
        try:
            prepared_request(EngineCommandFailed,
                             href=self._link('generate_snapshot'), 
                             filename=filename
                             ).read()
        except IOError as e:
            raise EngineCommandFailed("Generate snapshot failed: {}"
                                      .format(e))
           
    def snapshots(self):
        """ 
        References to policy based snapshots for this engine, including
        the date the snapshot was made

        :return: list :py:class:`smc.core.engine.Snapshot`
        :raises: :py:class:`smc.api.exceptions.EngineCommandFailed`
        """
        return [Snapshot(meta=Meta(**snapshot))
                for snapshot in self._get_resource_by_link('snapshots')]

class InternalGateway(SubElement):
    """ 
    InternalGateway represents the engine side VPN configuration
    This defines settings such as setting VPN sites on protected
    networks and generating certificates.
    This is defined under Engine->VPN within SMC.
    Since each engine has only one internal gateway, this resource
    is loaded immediately when called through engine.internal_gateway
    
    This is a resource of an Engine as it defines engine specific VPN 
    gateway settings::
    
        engine.internal_gateway.describe()
    
    :ivar href: location of this internal gateway
    :ivar etag: etag of internal gateway
    :ivar vpn_site: vpn site object
    :ivar internal_endpoint: interface endpoint mappings (where to enable VPN) 
    """
    def __init__(self, meta=None, **kwargs):
        super(InternalGateway, self).__init__(meta)
        pass

    @property
    def vpn_site(self):
        """
        Retrieve VPN Site information for this internal gateway
        
        Find all configured sites for engine::
        
            for site in engine.internal_gateway.vpn_site.all():
                print site

        :return: :py:class:`smc.vpn.elements.VPNSite`
        """
        return VPNSite(meta=Meta(href=self._link('vpn_site')))
    
    @property
    def internal_endpoint(self):
        """
        Internal Endpoint setting VPN settings to the interface
        
        Find all internal endpoints for an engine::
        
            for x in engine.internal_gateway.internal_endpoint.all():
                print x

        :return: list :py:class:`smc.vpn.elements.InternalEndpoint`
        """
        return InternalEndpoint(meta=Meta(href=self._link('internal_endpoint')))
    
    def gateway_certificate(self):
        """
        :return: list
        """
        return self._get_resource_by_link('gateway_certificate')
    
    def gateway_certificate_request(self):
        """
        :return: list
        """
        return self._get_resource_by_link('gateway_certificate_request')   
    
    def generate_certificate(self, certificate_request):
        """
        Generate an internal gateway certificate used for VPN on this engine.
        Certificate request should be an instance of VPNCertificate.

        :param: :py:class:`~smc.vpn.elements.VPNCertificate` certificate_request: 
                certificate request created
        :return: None
        :raises: :py:class:`smc.api.exceptions.CertificateError`
        """
        prepared_request(CertificateError,
                         href=self._link('generate_certificate'),
                         json=vars(certificate_request)).create()

class InternalEndpoint(SubElement):
    """
    InternalEndpoint lists the VPN endpoints either enabled or disabled for
    VPN. You should enable the endpoint for the interface that will be the
    VPN endpoint. You may also need to enable NAT-T and ensure IPSEC is enabled.
    This is defined under Engine->VPN->EndPoints in SMC. This class is a property
    of the engines internal gateway and not accessed directly.
    
    To see all available internal endpoint (VPN gateways) on a particular
    engine, get the engine context first::
        
        engine = Engine('myengine')
        for endpt in engine.internal_gateway.internal_endpoint.all():
            print endpt
    
    :ivar deducted_name: name of the endpoint is based on the interface
    :ivar dynamic: True|False
    :ivar enabled: True|False
    :ivar ipsec_vpn: True|False
    :ivar nat_t: True|False
    
    :param href: pass in href to init which will have engine insert location  
    """
    def __init__(self, meta=None):
        super(InternalEndpoint, self).__init__(meta)
        pass
    
    def all(self):
        """
        Return all internal endpoints
        
        :return: list :py:class:`smc.core.engine.InternalEndpoint`
        """
        return [InternalEndpoint(meta=Meta(**ep))
                for ep in self._get_resource(self.href)]
        
class VirtualResource(SubElement):
    """
    A Virtual Resource is a container placeholder for a virtual engine
    within a Master Engine. When creating a virtual engine, each virtual
    engine must have a unique virtual resource for mapping. The virtual 
    resource has an identifier (vfw_id) that specifies the engine ID for 
    that instance. There is currently no modify_attribute method available
    for this resource.
    
    This is called as a resource of an engine. To view all virtual
    resources::
        
        for resource in engine.virtual_resource.all():
            print resource
            
    To create a new virtual resource::
    
        engine.virtual_resource.create(......)
    
    When class is initialized, meta data is passed in from the engine method. 
    This is used to get the entry point for an empty resource and when loading
    existing resources, provides name and href of the virtual resource. 
    
    :ivar name: name of virtual resource
    :ivar vfw_id: virtual resource id

    :param meta: meta is provided from the engine.virtual_resource method
    """
    def __init__(self, meta=None):
        super(VirtualResource, self).__init__(meta)
        pass 
   
    @property
    def vfw_id(self):
        return self.data.get('vfw_id')

    def create(self, name, vfw_id, domain='Shared Domain',
               show_master_nic=False, connection_limit=0):
        """
        Create a new virtual resource
        
        :param str name: name of virtual resource
        :param int vfw_id: virtual fw identifier
        :param str domain: name of domain to install, (default Shared)
        :param boolean show_master_nic: whether to show the master engine NIC ID's
               in the virtual instance
        :param int connection_limit: whether to limit number of connections for this 
               instance
        :return: str href: href location of new virtual resource
        """
        allocated_domain = domain_helper(domain)
        json = {'name': name,
                'connection_limit': connection_limit,
                'show_master_nic': show_master_nic,
                'vfw_id': vfw_id,
                'allocated_domain_ref': allocated_domain}
        
        return prepared_request(CreateElementFailed,
                                href=self.href,
                                json=json).create().href
    
    def all(self):
        """
        Return metadata for all virtual resources
        
            for resource in engine.virtual_resource.all():
                if resource.name == 've-6':
                    print resource.describe()
        
        :return: list VirtualResource
        """
        return [VirtualResource(meta=Meta(**resource))
                for resource in self._get_resource(self.href)]
