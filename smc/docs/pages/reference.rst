*********
Reference
*********

Base
----
 
.. automodule:: smc.base.model
	:members: ElementBase, Element, SubElement

Elements
--------
Elements used for various configuration areas within SMC. Element types are made up of
network, service groups and other.

Network
+++++++

.. automodule:: smc.elements.network

Host
****

.. autoclass:: Host
   :members:
   :show-inheritance:

Network
*******

.. autoclass:: Network
   :members:
   :show-inheritance:

AddressRange
************

.. autoclass:: AddressRange
   :members:
   :show-inheritance:

Router
******

.. autoclass:: Router
   :members:
   :show-inheritance:

DomainName
**********

.. autoclass:: DomainName 
   :members:
   :show-inheritance:

IPList
******

.. autoclass:: IPList
   :members:
   :show-inheritance:

URLListApplication
******************

.. autoclass:: URLListApplication
	:members:
	:show-inheritance:

Expression
**********

.. autoclass:: Expression
	:members:
	:show-inheritance:

Zone
****

.. autoclass:: Zone 
   :members:
   :show-inheritance:

Alias
*****

.. autoclass:: Alias
	:members:
	:show-inheritance:
   
Services
++++++++

.. automodule:: smc.elements.service

TCPService
**********

.. autoclass:: TCPService 
   :members:
   :show-inheritance:

UDPService
**********

.. autoclass:: UDPService 
   :members:
   :show-inheritance:
   
IPService
*********

.. autoclass:: IPService 
   :members:
   :show-inheritance:
   
EthernetService
***************

.. autoclass:: EthernetService 
   :members:
   :show-inheritance:
   
Protocol
********

.. autoclass:: Protocol 
   :members:
   :show-inheritance:
   
ICMPService
***********

.. autoclass:: ICMPService 
   :members:
   :show-inheritance:
   
ICMPIPv6Service
***************

.. autoclass:: ICMPIPv6Service 
   :members:
   :show-inheritance:

Groups
++++++

.. automodule:: smc.elements.group
	:members: GroupMixin

Group
*****

.. autoclass:: Group
   :members:
   :show-inheritance:  

ServiceGroup
************

.. autoclass:: ServiceGroup 
   :members:
   :show-inheritance:
   
TCPServiceGroup
***************

.. autoclass:: TCPServiceGroup 
   :members:
   :show-inheritance:

UDPServiceGroup
***************

.. autoclass:: UDPServiceGroup 
   :members:
   :show-inheritance:

IPServiceGroup
**************

.. autoclass:: IPServiceGroup 
   :members:
   :show-inheritance:

Other
+++++

.. automodule:: smc.elements.other

LogicalInterface
****************

.. autoclass:: LogicalInterface 
   :members:
   :show-inheritance:

MacAddress
**********

.. autoclass:: MacAddress 
   :members:
   :show-inheritance:

Location
********

.. autoclass:: Location 
   :members:
   :show-inheritance:

ContactAddress
**************

.. autoclass:: ContactAddress
	:members:

Engine
------

.. automodule:: smc.core.engine
   :members:
   :exclude-members: create, VirtualResource, InternalEndpoint, InternalGateway
   :show-inheritance:

Appliance Status
++++++++++++++++

.. autoclass:: smc.core.node.ApplianceStatus
	:members:

Interface Status
****************

.. autoclass:: smc.core.node.InterfaceStatus
	:members:

Hardware Status
***************

.. autoclass:: smc.core.node.HardwareStatus
	:members:
	
Dynamic Routing
+++++++++++++++
Represents classes responsible for configuring dynamic routing protocols

OSPF
****

.. automodule:: smc.routing.ospf
	:members:
	
AccessList
**********

.. automodule:: smc.routing.access_list
	:members:
	:show-inheritance:

PrefixList
**********

.. automodule:: smc.routing.prefix_list
	:members:
	:show-inheritance:

Interfaces
++++++++++
Represents classes responsible for configuring interfaces on engines

.. automodule:: smc.core.interfaces
	:members: Interface
	:exclude-members: modify_interface

.. autoclass:: InterfaceCommon
	:members:
	
PhysicalInterface
*****************

.. autoclass:: PhysicalInterface
    :members: 
    :show-inheritance:

PhysicalVlanInterface
*********************

.. autoclass:: PhysicalVlanInterface
	:members:
	:show-inheritance:

VirtualPhysicalInterface
************************

.. autoclass:: VirtualPhysicalInterface
   :members:
   :show-inheritance:

TunnelInterface
***************

.. autoclass:: TunnelInterface
    :members:
    :show-inheritance:
 
Sub-Interfaces
++++++++++++++
Interfaces will have sub-interfaces that define aspects such as IP addresses,
VLANs or cluster virtual IPs. The sub-interface allows access to modify these
settings through property access.

.. automodule:: smc.core.sub_interfaces

ClusterVirtualInterface
***********************

.. autoclass:: ClusterVirtualInterface
	:members:
	:exclude-members: create

InlineInterface
***************

.. autoclass:: InlineInterface
   :members:
   :exclude-members: create
   
CaptureInterface
****************

.. autoclass:: CaptureInterface
	:members:
	:exclude-members: create

NodeInterface
*************

.. autoclass:: NodeInterface
	:members:
	:exclude-members: create

SingleNodeInterface
*******************

.. autoclass:: SingleNodeInterface
	:members:
	:show-inheritance:
	:exclude-members: create, create_dhcp
	
InternalEndpoint
++++++++++++++++

.. autoclass:: smc.core.engine.InternalEndpoint
   :members:
   :show-inheritance:
   
InternalGateway
+++++++++++++++

.. autoclass:: smc.core.engine.InternalGateway
   :members:
   :show-inheritance:

Node
++++

.. automodule:: smc.core.node
   :members: Node
   :exclude-members: create
   :show-inheritance:
 
Snapshot
++++++++

.. autoclass:: smc.core.resource.Snapshot
	:members:
	:show-inheritance:
	
VirtualResource
+++++++++++++++

.. autoclass:: smc.core.engine.VirtualResource
	:members:
	:show-inheritance:

Routing
+++++++

.. automodule:: smc.core.route
	:members:

Antispoofing
************

.. autoclass:: Antispoofing
	:members:
	:show-inheritance:

Routing
*******

.. autoclass:: Routing
	:members:
	:show-inheritance:
	
Routes
******

.. autoclass:: Routes
	:members:

Engine Types
------------

.. automodule:: smc.core.engines
   :members:
   :undoc-members:

IPS
+++

.. autoclass:: IPS
   :members:

Layer3Firewall
++++++++++++++

.. autoclass:: Layer3Firewall
   :members:
   
Layer2Firewall
++++++++++++++

.. autoclass:: Layer2Firewall
   :members:

Layer3VirtualEngine
+++++++++++++++++++

.. autoclass:: Layer3VirtualEngine
   :members:

FirewallCluster
+++++++++++++++

.. autoclass:: FirewallCluster
   :members:

MasterEngine
++++++++++++

.. autoclass:: MasterEngine
   :members:

MasterEngineCluster
+++++++++++++++++++

.. autoclass:: MasterEngineCluster
	:members:

Policy
------

.. automodule:: smc.policy.policy
   :members:
   :show-inheritance:

FirewallPolicy
++++++++++++++

.. automodule:: smc.policy.layer3
   :members:
   :show-inheritance:

Layer2Policy
++++++++++++

.. automodule:: smc.policy.layer2
   :members:
   :show-inheritance:

IPSPolicy
+++++++++

.. automodule:: smc.policy.ips
   :members:
   :show-inheritance:

InspectionPolicy
++++++++++++++++

.. autoclass:: smc.policy.policy.InspectionPolicy
   :members:
   :show-inheritance:

FileFilteringPolicy
+++++++++++++++++++

.. automodule:: smc.policy.file_filtering
   :members:
   :show-inheritance:

Policy Rules
------------
Represents classes responsible for configuring rule types.

.. automodule:: smc.policy.rule

Rule
++++

.. autoclass:: Rule
	:members:
	:show-inheritance:

IPv4Rule
********

.. autoclass:: IPv4Rule
   :members:
   :show-inheritance:

IPv4Layer2Rule
**************

.. autoclass:: IPv4Layer2Rule
   :members:
   :show-inheritance:
  
EthernetRule
************

.. autoclass:: EthernetRule
   :members:
   :show-inheritance:

IPv6Rule
********

.. autoclass:: IPv6Rule
   :members:
   :show-inheritance:

NATRule
+++++++

.. autoclass:: smc.policy.rule_nat.NATRule
	:members:
	:show-inheritance:

IPv4NATRule
***********

.. autoclass:: smc.policy.rule_nat.IPv4NATRule
   :members:
   :show-inheritance:

IPv6NATRule
***********

.. autoclass:: smc.policy.rule_nat.IPv6NATRule
   :members:
   :show-inheritance:
    
RuleElements
++++++++++++

.. automodule:: smc.policy.rule_elements
.. autoclass:: smc.policy.rule_elements.RuleElement
	:members:
	
Source
******

.. autoclass:: Source
	:members:
	:show-inheritance:
	
Destination
***********

.. autoclass:: Destination
	:members:
	:show-inheritance:
	
Service
*******

.. autoclass:: Service
	:members:
	:show-inheritance:
	
Action
******

.. autoclass:: Action
	:members:
	:show-inheritance:
	
ConnectionTracking
******************

.. autoclass:: ConnectionTracking
	:members:
	:show-inheritance:
	
LogOptions
**********

.. autoclass:: LogOptions
	:members:
	:show-inheritance:
	
AuthenticationOptions
*********************

.. autoclass:: AuthenticationOptions
	:members:
	:show-inheritance:

NATRuleElements
+++++++++++++++

.. automodule:: smc.policy.rule_nat
.. autoclass:: NAT
	:members:

DynamicSourceNAT
****************

.. autoclass:: DynamicSourceNAT
	:members:
	:show-inheritance:
	
StaticSourceNAT
***************

.. autoclass:: StaticSourceNAT
	:members:
	:show-inheritance:
	
DynamicSourceNAT
****************

.. autoclass:: DynamicSourceNAT
	:members:
	:show-inheritance:

VPN
---
Represents classes responsible for configuring VPN settings such as VPN external
gateways, VPN sites, VPN Certificate and VPN Policy

VPNPolicy
+++++++++

.. automodule:: smc.vpn.policy
   :members:
   :show-inheritance: 
 
ExternalGateway
+++++++++++++++

.. autoclass:: smc.vpn.elements.ExternalGateway
   :members:
   :show-inheritance:
   
ExternalEndpoint
++++++++++++++++

.. autoclass:: smc.vpn.elements.ExternalEndpoint
   :members:
   :show-inheritance:
   
VPNSite
+++++++

.. autoclass:: smc.vpn.elements.VPNSite
   :members:
   :show-inheritance:

VPNCertificate
++++++++++++++

.. autoclass:: smc.vpn.elements.VPNCertificate
   :members:
   :show-inheritance:

Administration
--------------

.. automodule:: smc.administration.system
	:members:

Tasks
+++++

.. automodule:: smc.administration.tasks
    :members: TaskMonitor, TaskDownload, Task, task_history, task_status

Updates
++++++++

.. automodule:: smc.administration.updates
	:members: PackageMixin

EngineUpgrade
*************

.. autoclass:: EngineUpgrade
	:members:
	:show-inheritance:
	
PackageUpdate
*************

.. autoclass:: UpdatePackage
	:members:
	:show-inheritance:

License
+++++++

.. automodule:: smc.administration.license
	:members:
	
AccessControlList
+++++++++++++++++

.. autoclass:: smc.administration.access_rights.AccessControlList
	:members:
	:show-inheritance:
	
Users
+++++

.. autoclass:: smc.elements.user.UserCommon
	:members:

.. automodule:: smc.elements.user
   :members:
   :show-inheritance:
 
Collection
----------

.. automodule:: smc.elements.collection
   :members:

Search
------

.. automodule:: smc.actions.search
   :members:
     
Session
-------

.. automodule:: smc.api.session
.. autoclass:: Session
   :members: login, logout, api_version, url, api_key, session, session_id

SMCResult
---------
Most operations being performed that involve REST operations will return an
SMCResult object. This object will hold attributes that are useful to determine
if the operation was successful and if not, the reason.

.. automodule:: smc.api.web
	:members: SMCResult

Exceptions
----------
Exceptions thrown throughout smc-python. Be sure to check functions or class methods
that have raises documentation. All exception classes subclass SMCException

.. automodule:: smc.api.exceptions
   :members:
   :show-inheritance:
