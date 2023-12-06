#!/usr/bin/python3

import unittest
import copy
import json
import os

from pathlib import Path
from v1.schema_utils.util import ReferenceRetriever
from v1.policy_manager.validatepolicy import PolicyManagerStringBuilder

import referencing
import jsonschema

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
        "policies":          {},
        "rules":             {}
    }
    
    @classmethod
    def setUpClass(cls):
        """
        setUpClass runs before all tests. Grabs file information, using some defaults if the environment variables 
        fail for any reason. Then performs the regular jsonschema.validate, to check against the schema. This errors 
        out, so any follow-up tests won't run
        """
        current_directory = os.path.dirname(os.path.realpath(__file__))
        
        if "JSON_FILE" in os.environ and os.environ["JSON_FILE"] != "":
            json_filename = os.environ["JSON_FILE"]
        else:
            json_filename = os.path.join(current_directory, cls.JSON_FILENAME_DEFAULT)
            print("WARNING: Using default json filename:" + str(json_filename))
        with open(json_filename, "r") as json_fp:
            cls.json_data = json.load(json_fp)
            
        if "SCHEMA_FILE" in os.environ and os.environ["SCHEMA_FILE"] != "":
            schema_filename = os.environ["SCHEMA_FILE"]
        else:
            schema_filename = os.path.join(current_directory, cls.SCHEMA_FILENAME_DEFAULT)
            print("WARNING: Using default schema filename:" + str(schema_filename))
        with open(schema_filename, "r") as schema_fp:
            schema_data = json.load(schema_fp)

        schema_file = Path(schema_filename)
        retriever = ReferenceRetriever(schema_file.parent.resolve())
        resource = referencing.Resource.from_contents(schema_data)

        try:
            # Add the resource to a new registry
            registry = resource @ referencing.Registry(retrieve=retriever.retrieve)  
            jsonschema.validate(instance=cls.json_data, schema=resource.contents, registry=registry)
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
                
    def get_condition_ids_referenced_in_policies(self):
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
            for condition in policy["conditions"]:
                ids_in_policies.append(condition)
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_policies))
                
    def get_rule_ids_in_policies(self):
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
            for rule in policy["rules"]:
                ids_in_policies.append(rule)
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_policies))

    def get_configuration_ids_in_rules(self):
        """
        Grab child object ids from rules either under actions or policies)

        Returns:
            list: unique list of id's under policies/child_obj
        """
        ids_in_rules = []
        for rule in self.json_rules:
            action = rule["action"]
            if "configuration_id" in action:
                ids_in_rules.append(action["configuration_id"])
            elif "policy" in action:
                ids_in_rules.append(action["policy"])
    
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_rules))
                
    def get_condition_ids_referenced_in_rules(self):
        """
        Grab child object ids from rules either under actions or policies)

        Returns:
            list: unique list of id's under policies/child_obj
        """
        ids_in_rules = []
        for rule in self.json_rules:
            ids_in_rules.extend(rule["conditions"])
    
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_rules))
                
    def get_ids_in_condition_objs(self):
        """
        Grabs ids from condition objs. Relatively easy, but done in multiple places, so turned into a method

        Returns:
            list: unique list of id's under condition objects
        """
        ids_in_condition_objs = [condition_obj["id"] for condition_obj in self.json_condition_objs]
        return list(set(ids_in_condition_objs))
    
    def get_condition_ids_referenced_in_condition_groups(self):
        """
        Grabs all of the condition ids referenced in conditions_groups which might not otherwise be referenced
        """
        ids_referenced = []
        for condition_group in self.json_condition_groups:
            ids_referenced.extend(condition_group["items"])
        return ids_referenced

    
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
        
        ids_in_object_groups = [object_group["id"] for object_group in self.json_object_groups]
        self.assertEqual(len(ids_in_object_groups), len(set(ids_in_object_groups)))
        
        ids_in_condition_objs = [condition_obj["id"] for condition_obj in self.json_condition_objs]
        self.assertEqual(len(ids_in_condition_objs), len(set(ids_in_condition_objs)))
        
        ids_in_condition_groups = [condition_group["id"] for condition_group in self.json_condition_groups]
        self.assertEqual(len(ids_in_condition_groups), len(set(ids_in_condition_groups)))
        
        ids_in_policies = [policy["id"] for policy in self.json_policies]
        self.assertEqual(len(ids_in_policies), len(set(ids_in_policies)))

        ids_in_rules = [rule["id"] for rule in self.json_rules]
        self.assertEqual(len(ids_in_rules), len(set(ids_in_rules)))

    def test_condition_ids_in_policies_rules_condition_groups(self):
        """
        Tests that any condition id's under policies, rules or conditiongroups exist in conditions (but not the other way around)
        """
        ids_referenced = self.get_condition_ids_referenced_in_policies()
        ids_referenced += self.get_condition_ids_referenced_in_rules()
        ids_referenced += self.get_condition_ids_referenced_in_condition_groups()
        ids_referenced = list(set(ids_referenced))
            
        # ids in configurations are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_conditions = [condition["id"] for condition in self.json_condition_objs]
        ids_in_conditions += [condition["id"] for condition in self.json_condition_groups]
        ids_in_conditions = list(set(ids_in_conditions))

        # check that all id's under policies are also under configurations
        ids_contained = all(i in ids_in_conditions for i in ids_referenced)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between policies/rules and conditions.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_conditions, ids_referenced, "condition_objects")
        
    def test_rule_ids_in_policies(self):
        """
        Tests that any rule  id's under policies exist in rules (but not the other way around)
        """
        ids_in_policies = self.get_rule_ids_in_policies()
            
        ids_in_rules = [rule["id"] for rule in self.json_rules]
        
        # check that all id's under policies are also under condition objects
        ids_contained = all(i in ids_in_rules for i in ids_in_policies)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between policies and condition objects.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_rules, ids_in_policies, "condition_objects")
        

    def test_configuration_ids_in_rules(self):
        """
        Tests that any configuration id's under rules exist in configurations (but not the other way around)
        """
        ids_in_rules = self.get_configuration_ids_in_rules()
            
        # ids in configurations are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_configurations = [configuration["id"] for configuration in self.json_configurations]
        ids_in_configurations = list(set(ids_in_configurations))
        
        # check that all id's under policies are also under configurations
        ids_contained = all(i in ids_in_configurations for i in ids_in_rules)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between rulesand configurations.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_configurations, ids_in_rules, "configurations")
        
    def test_object_ids_in_condition_objs_or_groups(self):
        """
        Tests that any object id's under condition objects exist in objects or object groups
        (but not the other way around)
        """
        # grab group ids from condition objs, which are individually nested within conditions
        ids_referenced = []
        for condition_obj in self.json_condition_objs:
            if "items" in condition_obj:
                for condition in condition_obj["items"]:
                    if "object" in condition:
                        ids_referenced += condition["object"]

        # ojects can also be referenced by object groups so this is needed to prevent orphans
        ids_refed_in_object_groups = []
        for object_group in self.json_object_groups:
            ids_refed_in_object_groups.extend(object_group["items"])

        ids_referenced.extend(ids_refed_in_object_groups)

        # we're only looking for matches, so strip duplicates to make the comparison work
        ids_referenced = list(set(ids_referenced))
        
        # ids in groups are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_objects = [object["id"] for object in self.json_objects]
        ids_in_objects += [ogroup["id"] for ogroup in self.json_object_groups]

        ids_in_objects = list(set(ids_in_objects))

        # check that all id's under condition objects are also under groups
        ids_contained = all(i in ids_in_objects for i in ids_referenced)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between condition objs and objects")
        
        # orphans the other way around are stored as warnings and printed late
        self.warnings_add_orphan(ids_in_objects, ids_referenced, "objects")
        
    def test_group_types(self):
        """
        Tests the types of each group to make sure that they are the correct format
        """
        for group in self.json_object_groups:
            idlen = len(group["id"])
            group_items = group["items"]
            self.assertIsNotNone(group_items, "Failed because a group has a null item list")
            self.assertNotEquals(len(group_items), 0, "Failed because a group has an empty item list")
            group_type = group["type"]
            valid_groups = ["ConditionGroup", "GeoipObjectGroup", "IpAddressObjectGroup", "ServiceEndpointObjectGroup"]
            isValid = group_type in valid_groups,
            self.assertTrue(isValid, "Failed because Object Group had unexpected type: " + group_type)
            if isValid:
                for item in group_items:
                    # Validate that the items are object IDs
                    self.assertEquals(len(item), idlen, "Failed because Object Group has a weird format: " + item + 
                                    " in group's items: " +  str(group_items))
                    
        for group in self.json_condition_groups:
            idlen = len(group["id"])
            group_items = group["items"]
            self.assertIsNotNone(group_items, "Failed because a group has a null item list")
            self.assertNotEquals(len(group_items), 0, "Failed because a group has an empty item list")
            for item in group_items:
                # Validate that the items are object IDs
                self.assertEquals(len(item), idlen, "Failed because Condition Group has a weird format: " + item + 
                                " in group's items: " +  str(group_items))


    @classmethod
    def tearDownClass(cls):
        """
        Prints the validated policy manager string. Should only print if validation was successful.
        """
        try:
            printer = PolicyManagerStringBuilder(cls.json_policies, cls.json_configurations, cls.json_condition_objs, 
                                                 cls.json_condition_groups, cls.json_objects, cls.json_object_groups,
                                                 cls.json_rules,  cls.warning_dict)
            print("--- Printing validated schema details ---")
            print(printer.buildAllPoliciesString())
        except KeyError as e:
            print("ERROR: Failed to print schema details after tests. Validation should also have failed.")
            print("\tThis error was: 'KeyError: " + str(e) + "'")
   
   
if __name__ == '__main__':
    unittest.main()
