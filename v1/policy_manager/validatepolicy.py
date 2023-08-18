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
policy_manager/policies/[either configurations or flows] have a match in configurations or flows (that is, there are 
no orphan id's)
"""
class TestPolicyManager(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT   = "test_settings.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    # class vars, begin uninitialized
    json_data           = ""
    json_policy_manager = ""
    json_configurations = ""
    json_groups         = ""
    json_flows          = ""
    json_policies       = ""
    
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

        # TODO RefResolver is deprecated, needs to be replaced soon
        # It also creates a pretty confusing error on jsonschema.validate when you use the wrong schema file, for example mfw_schema/v1/schema.json:
        # <urlopen error [Errno 2] No such file or directory: '{code location}/mfw_schema/v1/policy_manager/policy_manager/policy_manager_schema.json'>
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
        # Check that json_data has been initialized so we don't get errors
        if cls.json_data:
            cls.json_policy_manager = copy.deepcopy(cls.json_data["policy_manager"])
            cls.json_configurations = copy.deepcopy(cls.json_policy_manager["configurations"])
            cls.json_groups         = copy.deepcopy(cls.json_policy_manager["groups"])
            cls.json_flows          = copy.deepcopy(cls.json_policy_manager["flows"])
            cls.json_policies       = copy.deepcopy(cls.json_policy_manager["policies"])
        
    def test_configuration_ids_in_policies(self):
        """
        Tests that any id's which exist in policy_manager/policies/configurations also exist in each individual 
        policy_manager/configurations/id
        """
        # grab configuration ids from policies, which are stored as lists
        ids_in_policies = []
        for policy in self.json_policies:
            ids_in_policies += policy["configurations"]
        # we're only looking for matches, so strip duplicates and sort to make the comparison work
        ids_in_policies = sorted(list(set(ids_in_policies)))
            
        # ids in configurations are not a list, so grabbing them is easier. Strip duplicates and sort like above.
        ids_in_configurations = [configuration["id"] for configuration in self.json_configurations]
        ids_in_configurations = sorted(list(set(ids_in_configurations)))
        
        self.assertEqual(ids_in_policies, ids_in_configurations, "Failed due to a mismatch in ids between policies and configurations.")
        
    def test_flow_ids_in_policies(self):
        """
        Tests that any id's which exist in policy_manager/policies/flows also exist in each individual 
        policy_manager/flows/id
        """
        # grab flow ids from policies, which are stored as lists
        ids_in_policies = []
        for policy in self.json_policies:
            ids_in_policies += policy["flows"]
        # we're only looking for matches, so strip duplicates and sort to make the comparison work
        ids_in_policies = sorted(list(set(ids_in_policies)))
            
        # ids in flows are not a list, so grabbing them is easier. Strip duplicates and sort like above.
        ids_in_flows = [flow["id"] for flow in self.json_flows]
        ids_in_flows = sorted(list(set(ids_in_flows)))
        
        self.assertEqual(ids_in_policies, ids_in_flows, "Failed due to a mismatch in ids between policies and flows.")
        
    def test_group_ids_in_flows(self):
        """
        Tests that any id's which exist in policy_manager/flows/condition/groupid also exist in each individual 
        policy_manager/groups/id
        """
        # grab group ids from flows, which are individually nested within conditions
        ids_in_flows = []
        for flow in self.json_flows:
            ids_in_flows += [condition["groupid"] for condition in flow["conditions"] if "groupid" in condition]
        # we're only looking for matches, so strip duplicates and sort to make the comparison work
        ids_in_flows = sorted(list(set(ids_in_flows)))
        
        # ids in groups are not a list, so grabbing them is easier. Strip duplicates and sort like above.
        ids_in_groups = [group["id"] for group in self.json_groups]
        ids_in_groups = sorted(list(set(ids_in_groups)))
        
        self.assertEqual(ids_in_flows, ids_in_groups, "Failed due to a mismatch in ids between flows and groups")
        
    def test_group_properties(self):
        """
        Tests the properties of groups to make sure that they are the correct format
        """
        for group in self.json_groups:
            group_items = group["items"]
            self.assertIsNotNone(group_items, "Failed because a group has a null item list")
            self.assertNotEquals(len(group_items), 0, "Failed because a group has an empty item list")
            group_type = group["type"]
            if group_type == "GeoIPLocation":
                for item in group_items:
                    self.assertEquals(len(item), 2, "Failed because GeoIPLocation has a weird format: " + item + 
                                      " in group's items: " +  str(group_items))
            elif group_type == "InterfaceZone":
                pass # TODO can this be validated?
            elif group_type == "IPAddrList":
                pass # TODO can this be validated?
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
            printer = PolicyManagerStringBuilder(cls.json_policies, cls.json_configurations, cls.json_flows, cls.json_groups)
            print("--- Printing validated schema details ---")
            print(printer.buildAllPoliciesString())
        except KeyError as e:
            print("ERROR: Failed to print schema details after tests. Validation should also have failed.")
        
"""
PolicyManagerStringBuilder builds strings out of the passed .json information, composed of policies, configurations, 
flows, and groups. The intent is two-fold:
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
    def __init__(self, policies, configurations, flows, groups):
        """
        Initialize the object with the dictionaries to be printed, grabbed directly from the .json

        Args:
            policies (dict): A policy, which has id, name, description, enabled, configurations, and flows
            configurations (dict): A configuration, which has id, name, and description
            flows (dict): A flow, which has id, name, descriptions, and conditions. The conditions have type, op, and either value or a group
            groups (dict): A group, which has id, name, items, and type
        """
        self.policies = policies
        self.configurations = configurations
        self.flows = flows
        self.groups = groups
        
    def buildAllPoliciesString(self, prefix='', getNestedInfo=True):
        """
        Builds a string that represents all policies, in multiple lines. Call this to print the entirety of the policy manager.

        Args:
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (configurations and flows) should be returned. Defaults to True.

        Returns:
            string: A string representation of all policies. Alternatively, a string represntation of the entire policy manager
        """
        policies_arr = []
        for policy in self.policies:
            policies_arr.append(self.buildPolicyString(policy, prefix=prefix, getNestedInfo=getNestedInfo))
        return '\n'.join(policies_arr)
            
    def buildPolicyString(self, policy, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a policy and its properties. If getNestedInfo is included, will 
        print configurations and flows (and their nested info) linked to the "id" of the policy

        Args:
            policy (dict): The dict of a policy grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (configurations and flows) should be returned. Defaults to True.

        Returns:
            string: A string representation of a policy and its properties
        """
        policy_arr = [' '.join([prefix, "Policy:", policy["id"], "\tName:", policy["name"], "\tDesc:", policy["description"], "\tEnabled:", str(policy["enabled"])])]
        if getNestedInfo:
            for config_id in policy["configurations"]:
                for configuration in self.configurations:
                    if configuration["id"] == config_id:
                        policy_arr.append(self.buildConfigurationString(configuration, prefix='\t'))
            for flow_id in policy["flows"]:
                for flow in self.flows:
                    if flow["id"] == flow_id:
                        policy_arr.append(self.buildFlowString(flow, prefix='\t'))
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
    
    def buildAllFlowsString(self, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents all flows, in multiple lines

        Args:
            prefix (str, optional): A string to add to the beginning of each string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to True.

        Returns:
            string: A string representation of all flows and their properties
        """
        flows_arr = []
        for flow in self.flows:
            flows_arr.append(self.buildFlowString(flow, prefix=prefix, getNestedInfo=getNestedInfo))
        return '\n'.join(flows_arr)
            
    def buildFlowString(self, flow, prefix='', getNestedInfo=True):
        """
        Builds and returns a string that represents a flow and its properties. Prints more detailed information for the
        conditions in the flow. If getNestedInfo is included, will print groups linked to the "groupid" of the 
        conditions

        Args:
            flow (dict): A dict of a flow grabbed from the .json
            prefix (str, optional): A string to add to the beginning of the string. Usually \t. Defaults to ''.
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to True.

        Returns:
            string: A string representation of a flow and its properties
        """
        flow_arr = [' '.join([prefix, "Flow:", flow["id"], "\tName:,", flow["name"], "\tDescriptions:", flow["description"]])]
        for condition in flow["conditions"]:
            if "value" in condition:
                flow_arr.append(' '.join([prefix + '\t', "Condition:", condition["type"], condition["op"], str(condition["value"])]))
            else:
                flow_arr.append(' '.join([prefix + '\t', "Condition:", condition["type"], condition["op"], "\tGroup:", condition["groupid"]]))
                if getNestedInfo:
                    for group in self.groups:
                        if group["id"] == condition["groupid"]:
                            flow_arr.append(self.buildGroupString(group, prefix=prefix+"\t\t"))
        return '\n'.join(flow_arr)
                
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