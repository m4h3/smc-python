"""
Policy module represents the classes required to obtaining and manipulating 
policies within the SMC.

Policy is the top level base class for all policy subclasses such as 
:py:class:`smc.policy.layer3.FirewallPolicy`,
:py:class:`smc.policy.layer2.Layer2Policy`,
:py:class:`smc.policy.ips.IPSPolicy`,
:py:class:`smc.policy.inspection.InspectionPolicy`,
:py:class:`smc.policy.file_filtering.FileFilteringPolicy` 

Policy represents actions that are common to all policy types, however for
options that are not possible in a policy type, the method is overridden to
return None. For example, 'upload' is not called on a template policy, but 
instead on the policy referencing that template. Therefore 'upload' is 
overidden.

.. note:: It is not required to call open() and save() on SMC API >= 6.1. It is 
          also optional on earlier versions but if longer running operations are 
          needed, calling open() will lock the policy from test_external modifications
          until save() is called.
"""
from smc.api.exceptions import TaskRunFailed, PolicyCommandFailed,\
    ResourceNotFound
from smc.base.model import prepared_request, Meta
from smc.administration.tasks import task_handler, Task
from smc.base.model import Element
from smc.base.resource import Registry

class Policy(Element):
    """ 
    Policy is the base class for all policy types managed by the SMC.
    This base class is not intended to be instantiated directly.
    
    Subclasses should implement create(....) individually as each subclass will likely 
    have different input requirements.
    
    All generic methods that are policy level, such as 'open', 'save', 'force_unlock',
    'export', and 'upload' are encapsulated into this base class.
    """
    def __init__(self, name, meta=None):
        super(Policy, self).__init__(name, meta)
        pass
                                   
    def upload(self, engine, wait_for_finish=True):
        """ 
        Upload policy to specific device. This is an asynchronous call
        that will return a 'follower' link that can be queried to determine 
        the status of the task. 
        
        If wait_for_finish is False, the progress
        href is returned when calling this method. If wait_for_finish is
        True, this generator function will return the new messages as they
        arrive.

        :param engine: name of device to upload policy to
        :param wait_for_finish: whether to wait in a loop until the upload completes
        :return: generator with updates, or follower href if wait_for_finish=False
        """
        element = prepared_request(TaskRunFailed,
                                   href=self._link('upload'),
                                   params={'filter': engine}).create()
        
        return task_handler(Task(**element.json), 
                            wait_for_finish=wait_for_finish)

    def open(self):
        """ 
        Open policy locks the current policy, Use when making multiple
        edits that may require more time. Simple create or deleting elements
        generally can be done without locking via open.
        This is only used in SMC API 6.0 and below

        :raises: :py:class: `smc.api.exceptions.PolicyCommandFailed`
        :return: None
        """
        try:
            prepared_request(PolicyCommandFailed,
                             href=self._link('open')).create()
        except ResourceNotFound:
            pass

    def save(self):
        """ Save policy that was modified
        This is only used in SMC API v6.0 and below.

        :return: None
        """
        try:
            prepared_request(PolicyCommandFailed,
                             href=self._link('save')).create()
        except ResourceNotFound:
            pass

    def force_unlock(self):
        """ Forcibly unlock a locked policy 

        :return: :py:class:`smc.api.web.SMCResult`
        """
        prepared_request(PolicyCommandFailed,
                         href=self._link('force_unlock')).create()
    
    def search_rule(self, search):
        """
        Search a rule for a rule tag or name value
        Result will be the meta data for rule (name, href, type)
        
        Searching for a rule in specific policy::
        
            f = FirewallPolicy(policy)
            search = f.search_rule(searchable)
        
        :param str search: search string
        :return: list rule elements matching criteria
        """
        result = prepared_request(
                        href=self._link('search_rule'),
                        params={'filter': search}).read()
        if result.json:
            results = []
            for data in result.json:
                if data.get('type') == 'ips_ethernet_rule':
                    klazz = Registry['ethernet_rule']
                elif data.get('type') == 'ips_ipv4_access_rule':
                    klazz = Registry['layer2_ipv4_access_rule']
                else:
                    klazz = Registry[data.get('type')]
                results.append(klazz(meta=Meta(**data)))
                return results
        return []
   
    def search_category_tags_from_element(self):
        pass
    
    @property
    def template(self):
        """
        Each policy is based on a system level template policy that will
        be inherited. 
        
        :return: Template policy based on policy type
        """
        href = self.data.get('template') #href for template
        return Element.from_href(href)

    @property
    def inspection_policy(self):
        """
        Each policy is required to have a reference to an InspectionPolicy. 
        The policy may be "No Inspection" but will still exist as a 
        reference.
        
        :return: :py:class:`smc.policy.inspection_policy.InspectionPolicy`
        """
        href = self.data.get('inspection_policy')
        return Element.from_href(href)
    

class InspectionPolicy(Policy):
    """
    The Inspection Policy references a specific inspection policy that is a property
    (reference) to either a FirewallPolicy, IPSPolicy or Layer2Policy. This policy
    defines specific characteristics for threat based prevention. 
    In addition, exceptions can be made at this policy level to bypass scanning based
    on the rule properties.
    """
    typeof = 'inspection_template_policy'
    
    def __init__(self, name, meta=None):
        super(InspectionPolicy, self).__init__(name, meta)
        pass
    
    def export(self):
        #Not valid for inspection policy
        pass
    
    def upload(self):
        #Not valid for inspection policy
        pass