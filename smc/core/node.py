"""
Node level actions for an engine. Once an engine is loaded, all methods
and resources are available to that particular engine. 

For example, to load an engine and run node level commands::

    engine = Engine('myfw')
    for node in engine.nodes:
        node.reboot()
        node.bind_license()
        node.go_online()
        node.go_offline()
        ...
        ...
"""
from smc.base.util import save_to_file
from smc.api.exceptions import LicenseError, NodeCommandFailed, ResourceNotFound
from smc.base.model import SubElement, prepared_request
from collections import namedtuple

class Node(SubElement):
    """ 
    Node settings to make each engine node controllable individually.
    When Engine() is loaded, setattr will set all instance attributes
    with the contents of the node json. Very few would benefit from being
    modified with exception of 'name'. To change a top level attribute, you
    would call node.modify_attribute(name='value')
    Engine will have a 'has-a' relationship with node and stored as the
    nodes attribute
    
    Instance attributes:
    
    :ivar name: name of node
    :ivar type: type of node, i.e. firewall_node, etc
    :ivar nodeid: node id, useful for commanding engines
    :ivar disabled: whether node is disabled or not
    :ivar href: href of this resource
    """
    def __init__(self, meta=None):
        super(Node, self).__init__(meta)
        pass

    @property
    def type(self):
        """ 
        Node type
        """
        return self.meta.type

    @property
    def nodeid(self):
        """
        ID of this node
        """
        return self.attr_by_name('nodeid')

    @classmethod
    def create(cls, name, node_type, nodeid=1):
        """
        Create the node/s for the engine. This isn't called directly,
        instead it is used when engine.create() is called
        
        :param str name: name of node 
        :param str node_type: based on engine type specified 
        :param int nodeid: used to identify which node 
        """  
        node = {node_type: {
                    'activate_test': True,
                    'disabled': False,
                    'loopback_node_dedicated_interface': [],
                    'name': name + ' node '+str(nodeid),
                    'nodeid': nodeid}
                }
        return node

    def fetch_license(self):
        """ 
        Fetch the node level license
        
        :return: None
        :raises: :py:class:`smc.api.exceptions.LicenseError`
        """
        try:
            prepared_request(LicenseError,
                             href=self._link('fetch')).create()
        except ResourceNotFound:
            pass
    
    def bind_license(self, license_item_id=None):
        """ 
        Auto bind license, uses dynamic if POS is not found
        
        :param str license_item_id: license id
        :return: None
        :raises: :py:class:`smc.api.exceptions.LicenseError`
        """
        params = {'license_item_id': license_item_id}
        try:
            prepared_request(LicenseError,
                             href=self._link('bind'), 
                             params=params).create()
        except ResourceNotFound:
            pass
        
    def unbind_license(self):
        """ 
        Unbind a bound license on this node.
        
        :return: None
        :raises: :py:class:`smc.api.exceptions.LicenseError` 
        """
        try:
            prepared_request(LicenseError,
                             href=self._link('unbind')).create()
        except ResourceNotFound:
            pass

    def cancel_unbind_license(self):
        """ 
        Cancel unbind for license
        
        :return: None
        :raises: :py:class:`smc.api.exceptions.LicenseError`
        """
        try:
            prepared_request(LicenseError,
                             href=self._link('cancel_unbind')).create()
        except ResourceNotFound:
            pass

    def initial_contact(self, enable_ssh=True, time_zone=None, 
                        keyboard=None, 
                        install_on_server=None, 
                        filename=None):
        """ 
        Allows to save the initial contact for for the specified node
 
        :param boolean enable_ssh: flag to know if we allow the ssh daemon on the 
               specified node
        :param str time_zone: optional time zone to set on the specified node 
        :param str keyboard: optional keyboard to set on the specified node
        :param boolean install_on_server: optional flag to know if the generated configuration 
               needs to be installed on SMC Install server (POS is needed)
        :param str filename: filename to save initial_contact to
        :return: str initial contact text information
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed` 
        """
        try:
            result = prepared_request(href=self._link('initial_contact'),
                                      params={'enable_ssh': enable_ssh}).create()
            if result.content:
                if filename:
                    try:
                        save_to_file(filename, result.content)
                    except IOError as e:
                        raise NodeCommandFailed("Error occurred when attempting to "
                                                "save initial contact to file: {}"
                                                .format(e))
            return result.content
        except ResourceNotFound:
            raise NodeCommandFailed('Initial contact not supported on this node type')
    
    @property    
    def appliance_status(self):
        """ 
        Gets the appliance status for the specified node for the specific 
        supported engine 

        :return: list of status information
        """
        result = prepared_request(NodeCommandFailed,
                                  href=self._link('appliance_status')
                                  ).read()
        return ApplianceStatus(result.json)
    
    def status(self):
        """ 
        Basic status for individual node. Specific information such as node 
        name dynamic package version, configuration status, platform and version.

        :return: :py:class:`~NodeStatus`
        """
        result = prepared_request(NodeCommandFailed,
                                  href=self._link('status')).read()
        return NodeStatus(**result.json)

    def go_online(self, comment=None):
        """ 
        Executes a Go-Online operation on the specified node 
        typically done when the node has already been forced offline 
        via :func:`go_offline`

        :param str comment: (optional) comment to audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('go_online'),
                         params=params).update()

    def go_offline(self, comment=None):
        """ 
        Executes a Go-Offline operation on the specified node

        :param str comment: optional comment to audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('go_offline'),
                         params=params).update()

    def go_standby(self, comment=None):
        """ 
        Executes a Go-Standby operation on the specified node. 
        To get the status of the current node/s, run :func:`status`

        :param str comment: optional comment to audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('go_standby'),
                         params=params).update()

    def lock_online(self, comment=None):
        """ 
        Executes a Lock-Online operation on the specified node

        :param str comment: comment for audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('lock_online'),
                         params=params).update()

    def lock_offline(self, comment=None):
        """ 
        Executes a Lock-Offline operation on the specified node
        Bring back online by running :func:`go_online`.

        :param str comment: comment for audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('lock_offline'),
                         params=params).update()

    def reset_user_db(self, comment=None):
        """ 
        Executes a Send Reset LDAP User DB Request operation on this
        node.

        :param str comment: comment to audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        try:
            prepared_request(NodeCommandFailed,
                             href=self._link('reset_user_db'),
                             params=params).update()
        except ResourceNotFound:
            raise NodeCommandFailed('Reset userdb not supported on this node type')
    

    def diagnostic(self, filter_enabled=False):
        """ 
        Provide a list of diagnostic options to enable
        
        Get all diagnostic/debug settings::
            
            engine = Engine('myfw')
            for node in engine:
                for diag in node.diagnostic():
                    print diag
                    
        Add filter_enabled=True argument to see only enabled settings

        :param boolean filter_enabled: returns all enabled diagnostics
        :return: list of dict items with diagnostic info; key 'diagnostics'
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params={'filter_enabled': filter_enabled}
        try:
            result = prepared_request(NodeCommandFailed,
                                      href=self._link('diagnostic'),
                                      params=params).read()
            return [(Diagnostic(**diagnostic))
                    for diagnostic in result.json.get('diagnostics')]
        except ResourceNotFound:
            raise NodeCommandFailed('Diagnostic not supported on this node type: {}'
                                    .format(self.type))

    def send_diagnostic(self, diagnostic):
        """ 
        Enable or disable specific diagnostics on the node.
        Diagnostics enable additional debugging into the audit files. This is
        a dynamic setting that does not require a policy push once a setting 
        is enabled or disabled.
        
        Enable specific debug settings and apply to node::
        
            for node in engine.nodes:
                debug=[]
                for diag in node.diagnostic():
                    if diag.name == 'Protocol Agent':
                        diag.enable()
                        debug.append(diag)
                    elif diag.name == 'Packet filter':
                        diag.enable()
                        debug.append(diag)
            node.send_diagnostic(debug)
        
        :param list diagnostic: :py:class:`smc.core.node.Diagnostic` object
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        debug=[]
        for setting in diagnostic:
            debug.append(vars(setting))
        prepared_request(NodeCommandFailed,
                         href=self._link('send_diagnostic'),
                         json={'diagnostics': debug}).create()

    def reboot(self, comment=None):
        """ 
        Send reboot command to this node.

        :param str comment: comment to audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        prepared_request(NodeCommandFailed,
                         href=self._link('reboot'),
                         params=params).update()
 
    def sginfo(self, include_core_files=False,
               include_slapcat_output=False,
               filename='sginfo.gz'):
        """ 
        Get the SG Info of the specified node 

        :param include_core_files: flag to include or not core files
        :param include_slapcat_output: flag to include or not slapcat output
        """
        #params = {'include_core_files': include_core_files,
        #          'include_slapcat_output': include_slapcat_output}
        #result = prepared_request(href=self._link('sginfo'),
        #                          filename=filename).read()
        raise NotImplementedError
   
    def ssh(self, enable=True, comment=None):
        """
        Enable or disable SSH

        :param boolean enable: enable or disable SSH daemon
        :param str comment: optional comment for audit
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'enable': enable, 'comment': comment}
        try:
            prepared_request(NodeCommandFailed,
                             href=self._link('ssh'),
                             params=params).update()
        except ResourceNotFound:
            raise NodeCommandFailed('SSH not supported on this node type: {}'
                                    .format(self.type))

    def change_ssh_pwd(self, pwd=None, comment=None):
        """
        Executes a change SSH password operation on the specified node 

        :param str pwd: changed password value
        :param str comment: optional comment for audit log
        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        params = {'comment': comment}
        try:
            prepared_request(NodeCommandFailed,
                             href=self._link('change_ssh_pwd'),
                             params=params, 
                             json={'value': pwd}).update()
        except ResourceNotFound:
            raise NodeCommandFailed('Change SSH pwd not supported on this node type: {}'
                                    .format(self.type))

    def time_sync(self):
        """ 
        Send a time sync command to this node.

        :return: None
        :raises: :py:class:`smc.api.exceptions.NodeCommandFailed`
        """
        try:
            prepared_request(NodeCommandFailed,
                             href=self._link('time_sync')).update()
        except ResourceNotFound:
            raise NodeCommandFailed('Time sync not supported on this node type: {}'
                                    .format(self.type))
        
    def certificate_info(self):
        """ 
        Get the certificate info of this node. This can return None if the 
        engine type does not directly have a certificate, like a virtual engine
        where the master engine manages certificates.
        
        :return: dict with links to cert info
        """
        return self._get_resource_by_link('certificate_info')
    
class NodeStatus(object):
    """
    Node Status carrying attributes that can be checked easily
    
    :ivar dyn_up: dynamic update package version
    :ivar installed_policy: policy name
    :ivar name: name of engine
    :ivar platform: current underlying platform
    :ivar version: version of software installed
    
    :ivar configuration_status:
     
        Return values:
            * Initial no initial configuration file is yet generated.
            * Declared initial configuration file is generated.
            * Configured initial configuration is done with the engine.
            * Installed policy is installed on the engine.

    :ivar status:
    
        Return values:
            Not Monitored/Unknown/Online/Going Online/Locked Online/
            Going Locked Online/Offline/Going Offline/Locked Offline/
            Going Locked Offline/Standby/Going Standby/No Policy Installed
            
    :ivar state:
    
        Return values:
            INITIAL/READY/ERROR/SERVER_ERROR/NO_STATUS/TIMEOUT/
            DELETED/DUMMY
    """

    def __init__(self, **kwargs):
        self.configuration_status = None
        self.dyn_up = None
        self.installed_policy = None
        self.name = None
        self.platform = None
        self.state = None
        self.status = None
        self.version = None
        
        for k,v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, value):
        return None

class ApplianceStatus(object):
    """
    Appliance status provides information on hardware and
    interface data for the engine node. Call this on the
    engine node to retrieve statuses::
    
        engine = Engine('sg_vm')
        for x in engine.nodes:
            for status in x.appliance_status.hardware_status:
                print(status, status.items)
            for status in x.appliance_status.interface_status:
                print(status, status.items)
    """
    def __init__(self, data):
        self._data = data
        
    @property
    def hardware_status(self):
        """
        Hardware status for the engine
            
        :return: iterator :py:class:`smc.core.node.HardwareStatus`
        """
        return HardwareStatus(self._data.get('hardware_statuses'))
        
    @property
    def interface_status(self):
        """
        Interface status for the engine
        
        :return: iterator :py:class:`smc.core.node.InterfaceStatus`
        """
        return InterfaceStatus(self._data.get('interface_statuses'))
    
class HardwareStatus(object):
    """
    Represents the hardware status of the engine.
    """
    def __init__(self, data):
        self._data = data
            
    def __iter__(self):
        for states in self._data['hardware_statuses']:
            yield HardwareStatus(states)
        
    @property
    def name(self):
        return self._data.get('name')
        
    @property
    def items(self):
        """
        Items returns a namedtuple with label, param and value.
        Label is the key target, i.e. 'Root' in the case of file system.
        Param is the measured element, i.e. 'Partition Size'
        Value is the value of this combination.
            
        :return: list All status for given hardware selection
        """
        totals = []
        for item in self._data.get('items'):
            t = namedtuple('Status', 'label param value')
            for status in item.get('statuses'):
                totals.append(t(status.get('label'),
                                status.get('param'),
                                status.get('value')))
        return totals
        
    def __str__(self):
        return '{0}(name={1})'.format(self.__class__.__name__, self.name)
        
    def __repr__(self):
        return str(self)
        
class InterfaceStatus(object):
    """
    Interface status represents characteristics of
    interfaces on the appliance. These states are merely
    a view to the existing state
    """
    def __init__(self, data):
        self._data = data
            
    def __iter__(self):
        for states in self._data['interface_status']:
            yield InterfaceStatus(states)
    
    @property
    def name(self):
        return self._data.get('name')
        
    @property
    def items(self):
        """
        Interface items are returned as a named tuple and include
        interface id, name, status, link speed, mtu, interface media
        type and how the interface is used (i.e. Normal, Aggregate)
        
        :return: namedtuple of interface statuses
        """
        t = namedtuple('Status', 'interface_id name status speed mtu port type')
        return t(self._data.get('interface_id'),
                 self._data.get('name'),
                 self._data.get('status'),
                 self._data.get('speed_duplex'),
                 self._data.get('mtu'),
                 self._data.get('port'),
                 self._data.get('capability'))
                               
    def __str__(self):
        return '{0}(interface={1},name={2},status={3})'\
                .format(self.__class__.__name__, self._data.get('interface_id'), 
                        self.name, self._data.get('status'))
        
    def __repr__(self):
        return str(self)
            
class Diagnostic(object):
    """
    Diagnostic (debug) setting that can be enabled or disabled on the
    node. To retrieve the diagnostic options, get the engine context and
    iterate the available nodes::
    
        for node in engine.nodes:
            for diagnostic in node.diagnostics():
                print diagnostic
    
    This class is not called directly.
    :ivar str name: name of diagnostic
    :ivar boolean state: enabled or disabled
    
    :param diagnostic: diagnostic, called from node.diagnostic()
    """
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
    
    def enable(self):
        self.diagnostic['enabled'] = True
        
    def disable(self):
        self.diagnostic['enabled'] = False
    
    @property
    def name(self):
        return self.diagnostic.get('name')

    @property
    def state(self):
        return self.diagnostic.get('enabled')

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, 'name={},enabled={}'
                           .format(self.name, self.state))
