#!/usr/bin/python3
  
"""
PolicyManagerStringBuilder builds strings out of the passed .json information, composed of policies, configurations, 
condition objects, and groups. The intent is two-fold:
1. Use buildAllPoliciesString() prints a string representation of the entire policy manager after the .json is 
    validated and tested
2. debugging, so you can print individual items, groups of items, nested or non-nested info, etc.
Importantly, this object does not print anything. It returns a string which can then be printed. This is because 
printing is expensive in Python. Regular string concatenation is also very expensive, hence use of .join (which is much
faster)

Returns:
    PolicyManagerStringBuilder type: An object which returns built strings on the objects given to it
"""

# The json schema policy fields
ID_FIELD = "id"
ACTION_FIELD = "action"
CONDITIONS_FIELD = "conditions"
CONFIGURATION_ID_FIELD = "configuration_id"
DESCRIPTION_FIELD = "description"
ENABLED_FIELD = "enabled"
ITEMS_FIELD = "items"
NAME_FIELD = "name"
OBJECT_FIELD = "object"
OP_FIELD = "op"
ORPHANS_FIELD = "orphans"
POLICY_FIELD = "policy"
RULES_FIELD = "rules"
TYPE_FIELD = "type"
VALUE_FIELD = "value"

class PolicyManagerStringBuilder():
    def __init__(self, policies, configurations, condition_objs, condition_groups, objects, object_groups, rules, warnings_dict):
        """
        Initialize the object with the dictionaries to be printed, grabbed directly from the .json
        # NOTE spacing is done here with \t characters. However, the same can be done more cleanly with built-in Python
        # str methods: https://docs.python.org/3/library/stdtypes.html#str.ljust

        Args:
            policies (dict): A policy, which has id, name, description, enabled, configurations, and condition objects
            configurations (dict): A configuration, which has id, name, and description
            condition_objs (dict): A condition object, which has id, name, descriptions, and conditions. The conditions
                                    have type, op, and either value or a group
            groups (dict): A group, which has id, name, items, and type
            warnings (dict): A dict of warnings which will be printed (but don't fail tests)
        """
        self.policies = policies
        self.configurations = configurations
        self.condition_objs = condition_objs
        self.condition_groups = condition_groups
        self.objects = objects
        self.object_groups = object_groups
        self.rules = rules
        self.warnings_dict = warnings_dict
        
    def buildAllPoliciesString(self, prefix='', getNestedInfo=True, getWarnings=True):
        """
        Builds a string that represents all policies, in multiple lines. Call this to print the entirety of the policy 
        manager.

        Args:
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (configurations and condition objects) should be 
                                            returned. Defaults to True.

        Returns:
            string: A string representation of all policies. Alternatively, a string represntation of the entire policy
                    manager
        """
        policies_arr = []
        for policy in self.policies:
            policies_arr.append(self.buildPolicyString(policy, prefix=prefix, getNestedInfo=getNestedInfo))
        if getWarnings:
            for obj, warnings in self.warnings_dict.items():
                if ORPHANS_FIELD in warnings:
                    policies_arr.append(' '.join(["WARNING: Orphans found in", obj, ":", str(warnings[ORPHANS_FIELD])]))
        return '\n'.join(policies_arr)
            
    def buildPolicyString(self, policy, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a policy and its propertie                                                                                          s. If getNestedInfo is included, will 
        print configurations and condition objects (and their nested info) linked to the "id" of the policy

        Args:
            policy (dict): The dict of a policy grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (configurations and condition objects) should be 
                                            returned. Defaults to True.

        Returns:
            string: A string representation of a policy and its properties
        """
        policy_arr = [' '.join([prefix, "Policy:", policy[ID_FIELD], "\tName:", policy[NAME_FIELD], "\tDesc:", policy[DESCRIPTION_FIELD], "\tEnabled:", str(policy[ENABLED_FIELD])])]
        if getNestedInfo:
            if RULES_FIELD in policy:
                for rule_id in policy[RULES_FIELD]:
                    policy_arr.append("\Rule:")
                    for rule in self.rules:
                        if rule[ID_FIELD] == rule_id:
                            action = rule[ACTION_FIELD]
                            if CONFIGURATION_ID_FIELD in action:
                                for configuration in self.configurations:
                                    if configuration[ID_FIELD] == action[CONFIGURATION_ID_FIELD]:
                                        policy_arr.append(self.buildConfigurationString(configuration, prefix="\t\t"))
                                        break
                            if POLICY_FIELD in action:
                                for configuration in self.configurations:
                                    if configuration[ID_FIELD] == action[POLICY_FIELD]:
                                        policy_arr.append(self.buildConfigurationString(configuration, prefix="\t\t"))
                                        break
                            if CONDITIONS_FIELD in rule:
                                for condition_id in rule[CONDITIONS_FIELD]:
                                    for condition_obj in self.condition_objs:
                                        if condition_obj[ID_FIELD] == condition_id:
                                            policy_arr.append(self.buildConditionObjString(condition_obj, prefix="\t\t"))
                                            break
                                    for condition_obj in self.condition_groups:
                                        if condition_obj[ID_FIELD] == condition_id:
                                            policy_arr.append(self.buildConditionGroupString(condition_obj, prefix="\t\t"))
                                            break
            if CONDITIONS_FIELD in policy:
                for condition_id in policy[CONDITIONS_FIELD]:
                    for condition_obj in self.condition_objs:
                        if condition_obj[ID_FIELD] in condition_id:
                            policy_arr.append(self.buildConditionObjString(condition_obj, prefix='\t'))
                    for condition_obj in self.condition_groups:
                        if condition_obj[ID_FIELD] in condition_id:
                            policy_arr.append(self.buildConditionObjString(condition_obj, prefix='\t'))
        return '\n'.join(policy_arr)
                
    def buildAllConfigurationsString(self, prefix=''):
        """
        Builds a string that represents all configurations, in multiple lines

        Args:
            prefix (str, optional): A string to add to the beginning of each string. Usually \t Defaults to ''.

        Returns:
            string: A string representation of all configurations and their properties
        """
        configurations_arr = []
        for configuration in self.configurations:
            configurations_arr.append(self.buildConfigurationString(configuration, prefix=prefix))
        return '\n'.join(configurations_arr)
        
    def buildConfigurationString(self, configuration, prefix=''):
        """
        Builds and returns a string that represents a configuration and its properties

        Args:
            configuration (dict): The dict of a configuration grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.

        Returns:
            string: A string representation of a configuration and its properties
        """
        return ' '.join([prefix, "Config:", configuration[ID_FIELD], "\tName:", configuration[NAME_FIELD], "\tDesc:", configuration[DESCRIPTION_FIELD]])
    
    def buildAllConditionObjsString(self, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents all condition objects, in multiple lines

        Args:
            prefix (str, optional): A string to add to the beginning of each string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to 
                                            True.

        Returns:
            string: A string representation of all condition objects and their properties
        """
        condition_objs_arr = []
        for condition_obj in self.condition_objs:
            condition_objs_arr.append(self.buildConditionObjString(condition_obj, prefix=prefix, getNestedInfo=getNestedInfo))
        return '\n'.join(condition_objs_arr)
            
    def buildConditionObjString(self, condition_obj, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a condition object and its properties. Prints more detailed 
        information for the conditions in the condition object. If getNestedInfo is included, will print groups linked
        to the "groupid" of the conditions

        Args:
            condition object (dict): A dict of a condition object grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to 
                                            True.

        Returns:
            string: A string representation of a condition object and its properties
        """
        condition_obj_arr = [' '.join([prefix, "Condition Object:", condition_obj[ID_FIELD], "\tName:,", condition_obj[NAME_FIELD], "\tDescriptions:", condition_obj[DESCRIPTION_FIELD]])]
        for condition in condition_obj[ITEMS_FIELD]:
            if VALUE_FIELD in condition:
                condition_obj_arr.append(' '.join([prefix + '\t', "Condition:", condition[TYPE_FIELD], condition[OP_FIELD], str(condition[VALUE_FIELD])]))
            else:
                condition_obj_arr.append(' '.join([prefix + '\t', "Condition:", condition[TYPE_FIELD], condition[OP_FIELD], "\tObjects:", str(condition[OBJECT_FIELD])]))       
        return '\n'.join(condition_obj_arr)

    def buildConditionGroupString(self, condition_obj, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a condition group and its properties. 

        Args:
            condition group (dict): A dict of a condition object grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to 
                                            True.

        Returns:
            string: A string representation of a condition object and its properties
        """
        condition_group_array = [' '.join([prefix, "Condition Group:", condition_obj[ID_FIELD], "\tName:,", condition_obj[NAME_FIELD], "\tDescriptions:", condition_obj[DESCRIPTION_FIELD]])]
        for condition in condition_obj[ITEMS_FIELD]:
            condition_group_array.append(' '.join([prefix + '\t', "ConditionID:", condition]))
        return '\n'.join(condition_group_array)
                
    def buildAllGroupsString(self, prefix=''):
        """
        Builds and returns a string that represents all groups, in multiple lines

        Args:
            prefix (str, optional): A string to add to the beginning of each string. Usually \t. Defaults to ''.

        Returns:
            string: A string representation of all groups and their properties
        """
        groups_arr = []
        for group in self.groups:
            groups_arr.append(self.buildGroupString(group, prefix=prefix))
        return '\n'.join(groups_arr)
        
    def buildGroupString(self, group, prefix=''):
        """
        Builds and returns a string that represents a group and its properties

        Args:
            group (dict): The dict of a group grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.

        Returns:
            string: A string representation of a group and its properties
        """
        return ' '.join([prefix, "Group:", group[ID_FIELD], "\tName:", group[NAME_FIELD], "\tItems:", str(group[ITEMS_FIELD]), "\tType:", group[TYPE_FIELD]])

