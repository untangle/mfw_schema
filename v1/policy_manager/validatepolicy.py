#!/usr/bin/python3

import copy
import os
import unittest

from v1.schema_utils.util import SchemaValidator

# The json schema policy fields
ID_FIELD = "id"
ACTION_FIELD = "action"
CONDITIONS_FIELD = "conditions"
CONDITION_GROUPS_FIELD = "condition_groups"
CONFIGURATIONS_FIELD = "configurations"
CONFIGURATION_ID_FIELD = "configuration_id"
DESCRIPTION_FIELD = "description"
ENABLED_FIELD = "enabled"
ITEMS_FIELD = "items"
NAME_FIELD = "name"
OBJECTS_FIELD = "objects"
OBJECT_GROUPS_FIELD = "object_groups"
OBJECT_FIELD = "object"
OP_FIELD = "op"
POLICY_MANAGER_FIELD = "policy_manager"
POLICY_FIELD = "policy"
POLICIES_FIELD = "policies"
RULES_FIELD = "rules"
TYPE_FIELD = "type"
VALUE_FIELD = "value"


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
    warning_dict = {}
       
    @classmethod
    def setUpClass(cls):
        """
        setUpClass runs before all tests. Grabs file information, using some defaults if the environment variables 
        fail for any reason. Then performs the regular jsonschema.validate, to check against the schema. This errors 
        out, so any follow-up tests won't run
        """

        current_directory = os.path.dirname(os.path.realpath(__file__))
        schema_validator = SchemaValidator(current_directory, cls.JSON_FILENAME_DEFAULT, cls.SCHEMA_FILENAME_DEFAULT)
        
        if schema_validator.isValid():
            cls.json_data = schema_validator.getJsonData()
        else:
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
            cls.json_policy_manager = copy.deepcopy(cls.json_data[POLICY_MANAGER_FIELD])
            cls.json_configurations = copy.deepcopy(cls.json_policy_manager[CONFIGURATIONS_FIELD])
            cls.json_objects        = copy.deepcopy(cls.json_policy_manager[OBJECTS_FIELD])
            cls.json_object_groups  = copy.deepcopy(cls.json_policy_manager[OBJECT_GROUPS_FIELD])
            cls.json_condition_objs = copy.deepcopy(cls.json_policy_manager[CONDITIONS_FIELD])
            cls.json_condition_groups = copy.deepcopy(cls.json_policy_manager[CONDITION_GROUPS_FIELD])
            cls.json_rules          = copy.deepcopy(cls.json_policy_manager[RULES_FIELD])
            cls.json_policies       = copy.deepcopy(cls.json_policy_manager[POLICIES_FIELD])
            
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
                if key not in self.warning_dict:
                    self.warning_dict[key] = []
                self.warning_dict[key] += [possible_orphan]
                
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
            for condition in policy[CONDITIONS_FIELD]:
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
            for rule in policy[RULES_FIELD]:
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
            action = rule[ACTION_FIELD]
            if CONFIGURATION_ID_FIELD in action:
                ids_in_rules.append(action[CONFIGURATION_ID_FIELD])
            elif POLICY_FIELD in action:
                ids_in_rules.append(action[POLICY_FIELD])
    
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
            ids_in_rules.extend(rule[CONDITIONS_FIELD])
    
        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_rules))
                
    def get_ids_in_condition_objs(self):
        """
        Grabs ids from condition objs. Relatively easy, but done in multiple places, so turned into a method

        Returns:
            list: unique list of id's under condition objects
        """
        ids_in_condition_objs = [condition_obj[ID_FIELD] for condition_obj in self.json_condition_objs]
        return list(set(ids_in_condition_objs))
    
    def get_condition_ids_referenced_in_condition_groups(self):
        """
        Grabs all of the condition ids referenced in conditions_groups which might not otherwise be referenced
        """
        ids_referenced = []
        for condition_group in self.json_condition_groups:
            ids_referenced.extend(condition_group[ITEMS_FIELD])
        return ids_referenced

    
    # ~~~ TEST METHODS
        
    def test_base_id_uniqueness(self):
        """
        Tests that the base id's (e.g., policy/id or configuration/id) are all only used once at that level. That 
        means, for example, each group's id appears only once at that level (but of course may be referenced elsewhere,
        and that's enforced by other tests)
        """
        # Test by checking length of list against a set generated by the list (all of whose elements are unique)
        ids_in_configurations = [configuration[ID_FIELD] for configuration in self.json_configurations]
        self.assertEqual(len(ids_in_configurations), len(set(ids_in_configurations)))
        
        ids_in_objects = [object[ID_FIELD] for object in self.json_objects]
        self.assertEqual(len(ids_in_objects), len(set(ids_in_objects)))
        
        ids_in_object_groups = [object_group[ID_FIELD] for object_group in self.json_object_groups]
        self.assertEqual(len(ids_in_object_groups), len(set(ids_in_object_groups)))
        
        ids_in_condition_objs = [condition_obj[ID_FIELD] for condition_obj in self.json_condition_objs]
        self.assertEqual(len(ids_in_condition_objs), len(set(ids_in_condition_objs)))
        
        ids_in_condition_groups = [condition_group[ID_FIELD] for condition_group in self.json_condition_groups]
        self.assertEqual(len(ids_in_condition_groups), len(set(ids_in_condition_groups)))
        
        ids_in_policies = [policy[ID_FIELD] for policy in self.json_policies]
        self.assertEqual(len(ids_in_policies), len(set(ids_in_policies)))

        ids_in_rules = [rule[ID_FIELD] for rule in self.json_rules]
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
        ids_in_conditions = [condition[ID_FIELD] for condition in self.json_condition_objs]
        ids_in_conditions += [condition[ID_FIELD] for condition in self.json_condition_groups]
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
            
        ids_in_rules = [rule[ID_FIELD] for rule in self.json_rules]
        
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
        ids_in_configurations = [configuration[ID_FIELD] for configuration in self.json_configurations]
        ids_in_configurations = list(set(ids_in_configurations))
        
        # check that all id's under policies are also under configurations
        ids_contained = all(i in ids_in_configurations for i in ids_in_rules)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between rulesand configurations.")
        
        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_configurations, ids_in_rules, CONFIGURATIONS_FIELD)
        
    def test_object_ids_in_condition_objs_or_groups(self):
        """
        Tests that any object id's under condition objects exist in objects or object groups
        (but not the other way around)
        """
        # grab group ids from condition objs, which are individually nested within conditions
        ids_referenced = []
        for condition_obj in self.json_condition_objs:
            if ITEMS_FIELD in condition_obj:
                for condition in condition_obj[ITEMS_FIELD]:
                    if OBJECT_FIELD in condition:
                        ids_referenced += condition[OBJECT_FIELD]

        # ojects can also be referenced by object groups so this is needed to prevent orphans
        ids_refed_in_object_groups = []
        for object_group in self.json_object_groups:
            ids_refed_in_object_groups.extend(object_group[ITEMS_FIELD])

        ids_referenced.extend(ids_refed_in_object_groups)

        # we're only looking for matches, so strip duplicates to make the comparison work
        ids_referenced = list(set(ids_referenced))
        
        # ids in groups are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_objects = [object[ID_FIELD] for object in self.json_objects]
        ids_in_objects += [ogroup[ID_FIELD] for ogroup in self.json_object_groups]

        ids_in_objects = list(set(ids_in_objects))

        # check that all id's under condition objects are also under groups
        ids_contained = all(i in ids_in_objects for i in ids_referenced)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between condition objs and objects")
        
        # orphans the other way around are stored as warnings and printed late
        self.warnings_add_orphan(ids_in_objects, ids_referenced, OBJECTS_FIELD)
        
    def test_group_types(self):
        """
        Tests the types of each group to make sure that they are the correct format
        """
        for group in self.json_object_groups:
            idlen = len(group[ID_FIELD])
            group_items = group[ITEMS_FIELD]
            self.assertIsNotNone(group_items, "Failed because a group has a null item list")
            self.assertNotEquals(len(group_items), 0, "Failed because a group has an empty item list")
            group_type = group[TYPE_FIELD]
            valid_groups = ["ConditionGroup", "GeoipObjectGroup", "IpAddressObjectGroup", "ServiceEndpointObjectGroup"]
            isValid = group_type in valid_groups,
            self.assertTrue(isValid, "Failed because Object Group had unexpected type: " + group_type)
            if isValid:
                for item in group_items:
                    # Validate that the items are object IDs
                    self.assertEquals(len(item), idlen, "Failed because Object Group has a weird format: " + item + 
                                    " in group's items: " +  str(group_items))
                    
        for group in self.json_condition_groups:
            idlen = len(group[ID_FIELD])
            group_items = group[ITEMS_FIELD]
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
    def __init__(self, policies, configurations, condition_objs, condition_groups, objects, object_groups, rules, orphan_warnings):
        """
        Initialize the object with the dictionaries to be printed, grabbed directly from the .json

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
        self.orphans_warnings = orphan_warnings
        
    def buildAllPoliciesString(self, getNestedInfo=True, getWarnings=True):
        """
        Builds a string that represents all policies, in multiple lines. Call this to print the entirety of the policy 
        manager.

        Args:
            getNestedInfo (bool, optional): Whether nested info (configurations and condition objects) should be 
                                            returned. Defaults to True.

        Returns:
            string: A string representation of all policies. Alternatively, a string represntation of the entire policy
                    manager
        """
        policies_arr = []
        for policy in self.policies:
            policies_arr.append(self.buildPolicyString(policy, getNestedInfo=getNestedInfo))
        if getWarnings:
            for obj, warnings in self.orphans_warnings.items():
                    policies_arr.append(' '.join(["WARNING: Orphans found in", obj, ":", str(warnings)]))
        return '\n'.join(policies_arr)
            
    def buildPolicyString(self, policy, getNestedInfo=True):
        """
        Builds and returns a string that represents a policy and its propertie                                                                                          s. If getNestedInfo is included, will 
        print configurations and condition objects (and their nested info) linked to the "id" of the policy

        Args:
            policy (dict): The dict of a policy grabbed from the .json
            getNestedInfo (bool, optional): Whether nested info (configurations and condition objects) should be 
                                            returned. Defaults to True.

        Returns:
            string: A string representation of a policy and its properties
        """
        
        policy_json = {
            "Policy": policy["id"],
            "Name": policy["name"],
            "Desc": policy["description"],
            "Enabled": str(policy["enabled"]),
            "Rules": [],
            "Conditions": []
        }
        
        if getNestedInfo:
            if "rules" in policy:
                for rule_id in policy["rules"]:
                    rule_json=[]
                    for rule in self.rules:
                        if rule[ID_FIELD] == rule_id:
                            action = rule[ACTION_FIELD]
                            if CONFIGURATION_ID_FIELD in action:
                                for configuration in self.configurations:
                                    if configuration["id"] == action["configuration_id"]:
                                        rule_json.append(self.buildConfigurationString(configuration))
                                        break
                            if POLICY_FIELD in action:
                                for configuration in self.configurations:
                                    if configuration["id"] == action["policy"]:
                                        rule_json.append(self.buildConfigurationString(configuration))
                                        break
                            if CONDITIONS_FIELD in rule:
                                for condition_id in rule[CONDITIONS_FIELD]:
                                    for condition_obj in self.condition_objs:
                                        if condition_obj["id"] == condition_id:
                                            rule_json.append(self.buildConditionObjString(condition_obj))
                                            break
                                    for condition_obj in self.condition_groups:
                                        if condition_obj["id"] == condition_id:
                                            rule_json.append(self.buildConditionGroupString(condition_obj))
                                            break
                    policy_json["Rules"].append({"Rule" : rule_json})
            if "conditions" in policy:
                conditions_json = []
                for condition_id in policy["conditions"]:
                    for condition_obj in self.condition_objs:
                        if condition_obj["id"] in condition_id:
                            conditions_json.append(self.buildConditionObjString(condition_obj))
                    for condition_obj in self.condition_groups:
                        if condition_obj["id"] in condition_id:
                            conditions_json.append(self.buildConditionObjString(condition_obj))
                policy_json["Conditions"] = conditions_json
        
        return self.convert_json_to_string(policy_json)                    
        
    def buildConfigurationString(self, configuration):
        """
        Builds and returns a object that represents a configuration and its properties

        Args:
            configuration (dict): The dict of a configuration grabbed from the .json

        Returns:
            dict: A object representation of a configuration and its properties
        """
        
        return {
            "Config": {
                "ID": configuration["id"], 
                "Name" : configuration["name"], 
                "Desc": configuration["description"]
            }
        }
                
    def buildConditionObjString(self, condition_obj):
        """
        Builds and returns a object that represents a condition object and its properties. Prints more detailed 
        information for the conditions in the condition object. If getNestedInfo is included, will print groups linked
        to the "groupid" of the conditions

        Args:
            condition object (dict): A dict of a condition object grabbed from the .json
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to 
                                            True.

        Returns:
            dict: A object representation of a condition object and its properties
        """
        
        condition_json = {
            "ID": condition_obj["id"],
            "Name": condition_obj["name"], 
            "Descriptions": condition_obj["description"],
            "Conditions" : []
        }
        
        for condition in condition_obj["items"]:
            if "value" in condition:
                condition_json["Conditions"].append({"Condition" : ' '.join([condition["type"], condition["op"], str(condition["value"])])})
            else:
                condition_json["Conditions"].append({"Condition" : ' '.join([condition["type"], condition["op"] +",", "Objects :", str(condition["object"])])})
        
        return { "Condition Object" : condition_json}

    def buildConditionGroupString(self, condition_obj):
        """
        Builds and returns a object that represents a condition group and its properties. 

        Args:
            condition group (dict): A dict of a condition object grabbed from the .json
            getNestedInfo (bool, optional): Whether nested info (groups in this case) should be returned. Defaults to 
                                            True.

        Returns:
            string: A string representation of a condition object and its properties
        """
        condition_group = {
             "Condition Group": condition_obj["id"],
             "Name": condition_obj["name"],
             "Descriptions": condition_obj["description"],
             "ConditionIDs": str(condition_obj["items"])
        }
               
        return condition_group

    def convert_json_to_string(self, input, indent=0):
        """ 
            Converts a json to string, but removes curly braces, brackets and quotes.
            It recursively procces each field from json. If the field is dictionary or list, it displayes each member on sepparate line.
            At each new function call, the indentation is increased.

        Args:
            input (json): The input object to format.
            indent (int, optional): Number of spaces added before each line. Defaults to 0.

        Returns:
            string: The formated string
        """
        if isinstance(input, dict):  
            lines = []                       
            for k, v in input.items():
                # If the value from dict is another dict or list, print key and start on another line
                if isinstance(v, (dict, list)):
                    lines.append(f"{k}:\n{self.convert_json_to_string(v, indent + 2)}")
                else:
                    lines.append(f"{k}:{v}") 
            return "\n".join(" " * indent + line for line in lines)
        elif isinstance(input, list):
            lines = [self.convert_json_to_string(i, indent + 2) for i in input]
            return "\n".join(line for line in lines)
        else:
            return str(input) 
        
if __name__ == '__main__':
    unittest.main()
