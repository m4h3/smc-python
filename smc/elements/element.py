""" 
Element module holding logic to add network elements to SMC. 
All element's are a subclass of SMCElement (is-a). The create() function for each
element type class will generate the proper json for the given element type and returning that
element. The results can then be sent to the SMC through the :mod:`smc.api.common._create`. The
result will be the href for the newly created object.

See SMCElement for more details:
 
:class:`smc.elements.element.SMCElement` for more details.

"""
import util
import smc.actions.search as search

class SMCElement(object):
    """ SMCElement is the base class for all objects added, removed or
    modified through the SMC API.
    
    Common parameters that are needed are stored in this base class
    
    :param json: json data to be added or modified
    :param etag: returned during http get and used for modifying elements 
    :param type: type of object, used only for str printing from api.common
    :param name: name of object, used for str printing from api.common
    :param href: REQUIRED for create or modify operations to identify
    :param params: If additional parameters are needed for href
    the location of the element
    """
    def __init__(self):
        self.json = None
        self.etag = None
        self.type = None
        self.name = None
        self.href = None
        self.params = None 

    def create(self):
        return self
    
    @classmethod
    def factory(cls, name=None, href=None, etag=None, 
                _type=None, json=None, params=None):
        cls.name = name
        cls.href = href
        cls.etag = etag
        cls.type = _type
        cls.json = json
        cls.params = params
        return cls
        #element = SMCElement()
        #element.name = name
        #element.href = href
        #element.etag = etag
        #element._type = type
        #element.json = json
        #element.params = params
        #return element
    
    def _fetch_href(self):
        self.href = search.element_entry_point(self.type)
        
    def __str__(self):
        return "name: %s, type: %s" % (self.name, self.type)
  
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)  
        
class Host(SMCElement):
    """ Class representing a Host object used in access rules
    
    :param name: Name of element
    :param ip: ip address of host object
    :param secondary_ip: secondary ip address (optional)
    :param comment: optional comment
    
    Create a host element::
    
        host = Host('myhost', '1.1.1.1', '1.1.1.2', 'some comment for my host')
        host.create()
    """
    def __init__(self, name, ip, 
                 secondary_ip=None, comment=None):
        SMCElement.__init__(self)
        self.type = 'host'
        self.name = name
        self.ip = ip
        self.secondary_ip = []
        self.comment = comment
        if secondary_ip:
            self.secondary_ip.append(secondary_ip)
        
    def create(self):
        self.json = util.get_json_template('host.json')
        self.json['name'] = self.name
        self.json['address'] = self.ip
        self.json['comment'] = self.comment if self.comment is not None else ""
        if self.secondary_ip:
            for addr in self.secondary_ip:
                self.json['secondary'].append(addr)
        self._fetch_href()        
        return self
    
    def __str__(self):
        return "name: %s, type: %s, address: %s, secondary_ip: %s, comment: %s" % \
            (self.name, self.type, self.ip, self.secondary_ip, self.comment)  


class Service(SMCElement):
    """ Class representing a Service object used in access rules
    
    :param name: Name of element
    :param min_dst_port: port used for service
    :type min_dst_port: int
    :param proto: protocol for service (tcp,udp,icmp,ip,protocol)
    :param comment: optional comment
    
    Create a service element::
    
        service = Service('myservice', 6000, 'tcp', 'some comment')
        service.create()
    """
    def __init__(self, name, min_dst_port, href,
                 proto=None, comment=None):
        SMCElement.__init__(self)
        self.name = name
        self.type = proto if proto is not None else 'service'
        self.min_dst_port = min_dst_port
        self.proto = proto
        self.comment = comment
        self.services = ['tcp_service', 'icmp_service', 'icmp_ipv6_service', 'ip_service', 'protocol' \
                         'ethernet_service', 'udp_service']
        
    def create(self):
        self.json = util.get_json_template('service.json')
        self.json['name'] = self.name
        self.json['min_dst_port'] = self.min_dst_port
        self.json['comment'] = self.comment if self.comment is not None else ""
        self._fetch_href()      
        return self
    
    def __str__(self):
        return "name: %s, type: %s, port: %s" % (self.name, self.type, self.min_dst_port)
        
        
class Group(SMCElement):
    """ Class representing a Group object used in access rules
    
    :param name: Name of element
    :param members: group members by element names
    :type members: list or None
    :param comment: optional comment
    
    Create a group element::
    
        group = Group('mygroup') #no members
        group.create()
        
    Group with members::
    
        group = Group('mygroup', ['member1','member2'], 'and a comment')
        group.create()
    """
    def __init__(self, name, members=None, comment=None):
        SMCElement.__init__(self)       
        self.type = 'group'
        self.name = name
        self.members = []
        self.comment = comment
        if members:
            for member in members:
                self.members.append(member)
     
    def create(self):
        self.json = util.get_json_template('group.json')
        self.json['name'] = self.name
        self.json['element'] = self.members if self.members else []
        self.json['comment'] = self.comment if self.comment is not None else ""
        self._fetch_href()    
        return self
    
    def __str__(self):
        return "name: %s, type: %s, members: %s" % (self.name, self.type, len(self.members))


class IpRange(SMCElement):
    """ Class representing a IpRange object used in access rules
    
    :param name: Name of element
    :param iprange: iprange of element
    :type iprange: string
    :param comment: optional comment
    
    Create an address range element::
    
        iprange = IpRange('myrange', '1.1.1.1-1.1.1.5')
        iprange.create()
    """
    def __init__(self, name, iprange, comment=None):
        SMCElement.__init__(self)        
        self.type = 'address_range'
        self.name = name
        self.iprange = iprange
        self.comment = comment
        
    def create(self):
        self.json = util.get_json_template('iprange.json')
        self.json['name'] = self.name
        self.json['ip_range'] = self.iprange
        self.json['comment'] = self.comment if self.comment is not None else ""
        self._fetch_href()        
        return self

    def __str__(self):
        return "name: %s, type: %s, iprange: %s, comment: %s" % \
            (self.name, self.type, self.iprange, self.comment)
    
    
class Router(SMCElement):
    """ Class representing a Router object used in access rules
    
    :param name: Name of element
    :param address: ip address of host object
    :type address: string
    :param secondary_ip: secondary ip address (optional)
    :param comment: optional comment
    
    Create a router element::
    
        router = Router('myrouter', '1.2.3.4', comment='my router comment')
        router.create()
    """
    def __init__(self, name, address, 
                 secondary_ip=None, comment=None):
        SMCElement.__init__(self)       
        self.type = 'router'
        self.name = name
        self.address = address
        self.secondary_ip = []
        self.comment = comment
        if secondary_ip:
            self.secondary_ip.append(secondary_ip) 
    
    def create(self):       
        self.json = util.get_json_template('router.json')
        self.json['name'] = self.name
        self.json['address'] = self.address
        self.json['comment'] = self.comment if self.comment is not None else ""
        if self.secondary_ip:
            for addr in self.secondary_ip:
                self.json['secondary'].append(addr)
        self._fetch_href()           
        return self   

    def __str__(self):
        return "name: %s, type: %s, address: %s, secondary_ip: %s, comment: %s" % \
            (self.name, self.type, self.address, self.secondary_ip, self.comment)


class Network(SMCElement):
    """ Class representing a Network object used in access rules   
    
    :param name: Name of element
    :param ip4_network: network cidr
    :param comment: optional comment   
    
    .. note:: ip4_network can be cidr or full mask, /24 or /255.255.255.0
    
    Create a network element::
    
        networkwithcidr = Network('mynetwork', '2.2.2.0/24')
        networkwithcidr.create()
        
        or
        
        networkwithmask = Network('mynetwork', 2.2.2.0/255.255.255.0')
        networkwithmask.create()
    """
    def __init__(self, name, ip4_network, comment=None):
        SMCElement.__init__(self)        
        self.type  = 'network'
        self.name = name
        self.ip4_network = ip4_network
        self.comment = comment
    
    def create(self):        
        self.json = util.get_json_template('network.json')
        self.json['name'] = self.name
        self.json['ipv4_network'] = self.ip4_network
        self.json['comment'] = self.comment if self.comment is not None else ""
        self._fetch_href()
        return self

    def __str__(self):
        return "name: %s, type: %s, ip4_network: %s, comment: %s" % \
            (self.name, self.type, self.ip4_network, self.comment)

        