#!/usr/bin/python3

import copy
import json
import jsonschema
import os
import unittest

"""
TestPolicyManager tests all parts of the policy manager schema

First, it runs jsonschema.validate to check against the policy_manager_schema.json file
Second, it runs tests on things that the schema cannot check. Right now, that is only ensuring that all id's in 
policy_manager/policies/[either configurations or condition objects] have a match in configurations or condition 
objects (that is, there are no orphan id's)
"""
class TestPolicyManager(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT   = "test_settings.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    # class vars, begin uninitialized
    json_data           = ""
    json_policy_manager = ""
    json_configurations = ""
    json_objects        = ""
    json_object_groups  = ""
    json_condition_objs = ""
    json_condition_groups = ""
    json_policies       = ""
    warning_dict = {
        "configurations":    {},
        "condition_objects": {},
        "condition_groups":  {},
        "objects":           {},
        "object_groups":     {},
        "policies":          {}
    }
    
    @classmethod
    def setUpClass(cls):
        """
        setUpClass runs before all tests. Grabs file information, using some defaults if the environment variables 
        fail for any reason. Then performs the regular jsonschema.validate, to check against the schema. This errors 
        out, so the follow-up tests won't run
        """
        current_directory = os.path.dirname(os.path.realpath(__file__))
        try:
            json_filename   = os.environ["JSON_FILE"]
            schema_filename = os.environ["SCHEMA_FILE"]
        except KeyError:
            json_filename   = os.path.join(current_directory, cls.JSON_FILENAME_DEFAULT)
            schema_filename = os.path.join(current_directory, cls.SCHEMA_FILENAME_DEFAULT)
            print("ERROR: Failed to get filenames from environment variables. Using default filenames:")
            print("\tjson=" + str(json_filename))
            print("\tschema=" + str(schema_filename))

        with open(json_filename, "r") as json_fp:
            cls.json_data = json.load(json_fp)
        
        with open(schema_filename, "r") as schema_fp:
            schema_data = json.load(schema_fp)

        # NOTE RefResolver is deprecated, needs to be replaced soon
        # It also creates a pretty confusing error on jsonschema.validate when you use the wrong schema file, for 
        # example mfw_schema/v1/schema.json:
        # <urlopen error [Errno 2] No such file or directory: 
        # '{code location}/mfw_schema/v1/policy_manager/policy_manager/policy_manager_schema.json'>
        resolver = jsonschema.RefResolver('file://' + current_directory + '/', None)

        try:
            jsonschema.validate(cls.json_data, schema_data, resolver=resolver)
        except Exception as e:
            print(e)
            raise unittest.SkipTest("ERROR: Validation of schema failed. Skipping all tests and printing.")
        
        # Sets class variables in case they need to be accessed after initialization, but before tests
        cls.refresh_jsons()
    
    def setUp(self):
        """
        Runs before every test. Copies parts of the original json, so that they can be modified without worry
        """
        self.refresh_jsons()
        
    @classmethod
    def refresh_jsons(cls):
        """
        Copies json_data into variables, both before each test and as an initialization
        """
        if cls.json_data:
            cls.json_policy_manager = copy.deepcopy(cls.json_data["policy_manager"])
            cls.json_configurations = copy.deepcopy(cls.json_policy_manager["configurations"])
            cls.json_objects        = copy.deepcopy(cls.json_policy_manager["objects"])
            cls.json_object_groups  = copy.deepcopy(cls.json_policy_manager["object_groups"])
            cls.json_condition_objs = copy.deepcopy(cls.json_policy_manager["conditions"])
            cls.json_condition_groups = copy.deepcopy(cls.json_policy_manager["condition_groups"])
            cls.json_rules          = copy.deepcopy(cls.json_policy_manager["rules"])
            cls.json_policies       = copy.deepcopy(cls.json_policy_manager["policies"])
            
    # ~~~ HELPER METHODS

    def warnings_add_orphan(self, child_ids, parent_ids, key):
        """
        Adds an orphan to the warnings dict so it can be printed later

        Args:
            child_ids (list): list of id's from child, such as configuration (if policy is parent)
            parent_ids (list): list of id's from parent, such as condition object (if child is group)
            key (string): obj there's a warning about, such as group or configuration
        """
        for possible_orphan in child_ids:
            if possible_orphan not in parent_ids:
                if "orphans" not in self.warning_dict[key]:
                    self.warning_dict[key]["orphans"] = []
                self.warning_dict[key]["orphans"] += [possible_orphan]
                
    def get_ids_in_policies(self, child_objs):
        """
        Grab child object ids from policies either under services/child_obj or just child_objs (note, that the trailing
        's' does matter here!)

        Args:
            child_objs (string): either "configurations" or "condition_objects"

        Returns:
            list: unique list of id's under policies/child_obj
        """
        ids_in_policies = []
        for policy in self.json_policies:
            if "services" in policy:
                child_obj = child_objs[:-1] # strip 's' from end of string to follow services format
                ids_in_policies += [service[child_obj] for service in policy["services"] if child_obj in service]
            if child_objs in policy:
                ids_in_policies += policy[child_objs]
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_policies))
                
    def get_ids_in_condition_objs(self):
        """
        Grabs ids from condition objs. Relatively easy, but done in multiple places, so turned into a method

        Returns:
            list: unique list of id's under condition objects
        """
        ids_in_condition_objs = [condition_obj["id"] for condition_obj in self.json_condition_objs]
        return list(set(ids_in_condition_objs))
    
    # ~~~ TEST METHODS
        
    def test_base_id_uniqueness(self):
        """
        Tests that the base id's (e.g., policy/id or configuration/id) are all only used once at that level. That 
        means, for example, each group's id appears only once at that level (but of course may be referenced elsewhere,
        and that's enforced by other tests)
        """
        # Test by checking length of list against a set generated by the list (all of whose elements are unique)
        ids_in_configurations = [configuration["id"] for configuration in self.json_configurations]
        self.assertEqual(len(ids_in_configurations), len(set(ids_in_configurations)))
        
        ids_in_objects = [object["id"] for object in self.json_objects]
        self.assertEqual(len(ids_in_objects), len(set(ids_in_objects)))
        
        ids_in_condition_objs = [condition_obj["id"] for condition_obj in self.json_condition_objs]
        self.assertEqual(len(ids_in_condition_objs), len(set(ids_in_condition_objs)))
        
        ids_in_policies = [policy["id"] for policy in self.json_policies]
        self.assertEqual(len(ids_in_policies), len(set(ids_in_policies)))
        
    def test_configuration_ids_in_policies(self):
        """
        Tests that any configuration id's under policies exist in configurations (but not the other way around)
        """
        ids_in_policies = self.get_ids_in_policies("configurations")
            
        # ids in configurations are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_configurations = [configuration["id"] for configuration in self.json_configurations]
        ids_in_configurations = list(set(ids_in_configurations))
        
        # check that all id's under policies are also under configurations
        ids_contained = all(i in ids_in_configurations for i in ids_in_policies)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between policies and configurations.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_configurations, ids_in_policies, "configurations")
        
    def test_condition_obj_ids_in_policies(self):
        """
        Tests that any condition object id's under policies exist in configuration objects (but not the other way around)
        """
        ids_in_policies = self.get_ids_in_policies("condition_objs")
            
        ids_in_condition_objs = self.get_ids_in_condition_objs()
        
        # check that all id's under policies are also under condition objects
        ids_contained = all(i in ids_in_condition_objs for i in ids_in_policies)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between policies and condition objects.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_condition_objs, ids_in_policies, "condition_objects")
        
    def test_object_ids_in_condition_objs(self):
        """
        Tests that any group id's under condition objects exist in groups (but not the other way around)
        """
        # grab group ids from condition objs, which are individually nested within conditions
        ids_in_condition_objs = []
        for condition_obj in self.json_condition_objs:
            if "items" in condition_obj:
                for condition in condition_obj["items"]:
                    if "object" in condition:
                        ids_in_condition_objs += condition["object"]
#            ids_in_condition_objs += [condition["object"] for condition in condition_obj["conditions"] if "object" in condition]
        # we're only looking for matches, so strip duplicates to make the comparison work
        ids_in_condition_objs = list(set(ids_in_condition_objs))
        
        # ids in groups are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_objects = [object["id"] for object in self.json_objects]
        ids_in_objects += [object["id"] for object in self.json_object_groups]
        ids_in_objects = list(set(ids_in_objects))

        # check that all id's under condition objects are also under groups
        ids_contained = all(i in ids_in_objects for i in ids_in_condition_objs)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between condition objs and objects")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_objects, ids_in_condition_objs, "objects")
        
    def test_group_types(self):
        """
        Tests the types of each group to make sure that they are the correct format
        """
        for group in self.json_object_groups:
            group_items = group["items"]
            self.assertIsNotNone(group_items, "Failed because a group has a null item list")
            self.assertNotEquals(len(group_items), 0, "Failed because a group has an empty item list")
            group_type = group["type"]
            if group_type == "ConditionGroup":
                for item in group_items:
                    ids_in_condition_objs = self.get_ids_in_condition_objs()
                    self.assertIn(item, ids_in_condition_objs, "Failed because a ConditionGroup: " + item + 
                                  "is not in any condition object")
            elif group_type == "GeoIPLocation":
                for item in group_items:
                    self.assertEquals(len(item), 2, "Failed because GeoIPLocation has a weird format: " + item + 
                                      " in group's items: " +  str(group_items))
            elif group_type == "ServiceEndpoint":
                for item in group_items:
                    for key, value in item.items():
                        self.assertTrue(key == "protocol" or key == "port", "Failed because ServiceEndPoint had " +
                                        "unexpected pair: " + str({key:value}) + " in group's item: " + str(item))

    @classmethod
    def tearDownClass(cls):
        """
        Prints the validated policy manager string. Should only print if validation was successful.
        """
        try:
            print(cls.warning_dict)
            printer = PolicyManagerStringBuilder(cls.json_policies, cls.json_configurations, cls.json_condition_objs, cls.json_objects, cls.warning_dict)
            print("--- Printing validated schema details ---")
            print(printer.buildAllPoliciesString())
        except KeyError as e:
            print("ERROR: Failed to print schema details after tests. Validation should also have failed.")
            print("\tThis error was: 'KeyError: " + str(e) + "'")
        
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
class PolicyManagerStringBuilder():
    def __init__(self, policies, configurations, condition_objs, groups, warnings_dict):
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
        self.groups = groups
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
                if "orphans" in warnings:
                    policies_arr.append(' '.join(["WARNING: Orphans found in", obj, ":", str(warnings["orphans"])]))
        return '\n'.join(policies_arr)
            
    def buildPolicyString(self, policy, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a policy and its properties. If getNestedInfo is included, will 
        print configurations and condition objects (and their nested info) linked to the "id" of the policy

        Args:
            policy (dict): The dict of a policy grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (configurations and condition objects) should be 
                                            returned. Defaults to True.

        Returns:
            string: A string representation of a policy and its properties
        """
        policy_arr = [' '.join([prefix, "Policy:", policy["id"], "\tName:", policy["name"], "\tDesc:", policy["description"], "\tEnabled:", str(policy["enabled"])])]
        if getNestedInfo:
            if "services" in policy:
                for service in policy["services"]:
                    policy_arr.append("\tService:")
                    if "configuration" in service:
                        for configuration in self.configurations:
                            if configuration["id"] == service["configuration"]:
                                policy_arr.append(self.buildConfigurationString(configuration, prefix="\t\t"))
                    if "condition_object" in service:
                        for condition_obj in self.condition_objs:
                            if condition_obj["id"] == service["condition_object"]:
                                policy_arr.append(self.buildConditionObjString(condition_obj, prefix="\t\t"))
            if "configurations" in policy:
                for configuration in self.configurations:
                    if configuration["id"] in policy["configurations"]:
                        policy_arr.append(self.buildConfigurationString(configuration, prefix='\t'))
            if "condition_objects" in policy:
                for condition_obj in self.condition_objs:
                    if condition_obj["id"] in policy["condition_objects"]:
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
        return ' '.join([prefix, "Config:", configuration["id"], "\tName:", configuration["name"], "\tDesc:", configuration["description"]])
    
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
        condition_obj_arr = [' '.join([prefix, "Condition Object:", condition_obj["id"], "\tName:,", condition_obj["name"], "\tDescriptions:", condition_obj["description"]])]
        for condition in condition_obj["conditions"]:
            if "value" in condition:
                condition_obj_arr.append(' '.join([prefix + '\t', "Condition:", condition["type"], condition["op"], str(condition["value"])]))
            else:
                condition_obj_arr.append(' '.join([prefix + '\t', "Condition:", condition["type"], condition["op"], "\tGroup:", condition["object"]]))
                if getNestedInfo:
                    for group in self.groups:
                        if group["id"] == condition["object"]:
                            condition_obj_arr.append(self.buildGroupString(group, prefix=prefix+"\t\t"))
        return '\n'.join(condition_obj_arr)
                
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
        return ' '.join([prefix, "Group:", group["id"], "\tName:", group["name"], "\tItems:", str(group["items"]), "\tType:", group["type"]])

if __name__ == '__main__':
    unittest.main()
