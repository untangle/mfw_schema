# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

#!/usr/bin/python3
import copy
import json
import os
import unittest
from uuid import UUID
from pathlib import Path
import referencing
import jsonschema

from v1.schema_utils.util import ReferenceRetriever
"""
TestQuotaManager validates the quota_manager schema

Unlike other tests, this just validates the schema since there are no further required tests.
"""
class TestQuotaManager(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "quota_manager_test.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    # class vars, begin uninitialized
    json_data           = ""
    json_quota_manager  = ""
    json_configurations = ""
    json_exceed_actions = ""
    json_rules = ""
    json_rule_conditions = ""
    warning_dict = {
        "configurations":    {},
        "exceed_actions":    {},
        "rules":             {},
        "rule_conditions":   {},
        "rule_action":       {},
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

    def test_valid_ids(self):
        """
        Testing that each quota_manager lists configuration's id is a valid uuid
        """
        for configuration in self.json_data["quota_manager"]["configurations"]:
            id_val = configuration["id"]
            try:
                uuid_obj = UUID(id_val)
            except ValueError:
                self.fail("Failed due to an invalid ID in quota_manager configurations:" + id_val)

        for action in self.json_data["quota_manager"]["exceed_actions"]:
            id_val = action["id"]
            try:
                uuid_obj = UUID(id_val)
            except ValueError:
                self.fail("Failed due to an invalid ID in quota_manager exceed_actions: " + id_val)
        self.assertTrue(True)


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
            cls.json_quota_manager = copy.deepcopy(cls.json_data["quota_manager"])

            cls.json_configurations = copy.deepcopy(cls.json_quota_manager["configurations"])
            cls.json_exceed_actions = copy.deepcopy(cls.json_quota_manager["exceed_actions"])
            cls.json_rules  = copy.deepcopy(cls.json_quota_manager["rules"])

    # ~~~ HELPER METHODS
    def warnings_add_orphan(self, child_ids, parent_ids, key):
        """
        Adds an orphan to the warnings dict so it can be printed later

        Args:
            child_ids (list): list of id's from child, such as configuration (if rule is parent)
            parent_ids (list): list of id's from parent, such as configuration (if child is group)
            key (string): obj there's a warning about, such as group or configuration
        """
        for possible_orphan in child_ids:
            if possible_orphan not in parent_ids:
                if "orphans" not in self.warning_dict[key]:
                    self.warning_dict[key]["orphans"] = []
                self.warning_dict[key]["orphans"] += [possible_orphan]


    # ~~~ TEST METHODS

    def test_base_id_uniqueness(self):
        """
        Tests that the base id's (e.g., quota/id or configuration/id) are all only used once at that level. That
        means, for example, each group's id appears only once at that level (but of course may be referenced elsewhere,
        and that's enforced by other tests)
        """
        # Test by checking length of list against a set generated by the list (all of whose elements are unique)
        ids_in_configurations = [configuration["id"] for configuration in self.json_configurations]
        self.assertEqual(len(ids_in_configurations), len(set(ids_in_configurations)))

        ids_in_exceed_actions = [action["id"] for action in self.json_exceed_actions]
        self.assertEqual(len(ids_in_exceed_actions), len(set(ids_in_exceed_actions)))

        ids_in_rules = [rule["id"] for rule in self.json_rules]
        self.assertEqual(len(ids_in_rules), len(set(ids_in_rules)))


    def test_configuration_ids_in_quota_rules(self):
        """
        Tests that any configuration id's under quota rule's actions (but not the other way around)
        """
        ids_referenced = self.get_configuration_ids_referenced_in_rule_actions()
        ids_referenced = list(set(ids_referenced))

        # ids in configurations are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_configurations = [rules["id"] for rules in self.json_configurations]
        ids_in_configurations = list(set(ids_in_configurations))

        # check that all id's under rules are also under configurations
        ids_contained = all(i in ids_in_configurations for i in ids_referenced)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between rules and configurations.")

        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_configurations, ids_referenced, "configurations")

    def get_configuration_ids_referenced_in_rule_actions(self):
        """
        Grab child object ids from quota under rules

        Returns:
            list: unique list of id's under rule's action.
        """
        ids_in_rules = []
        for rule in self.json_rules:
            action = rule["action"]
            if "quota_id" in action:
                ids_in_rules.append(action["quota_id"])

        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_rules))

    def get_exceed_action_ids_in_quota_rules(self):
        """
        Grab child object ids from action under rules

        Returns:
            list: unique list of id's under rule's action
        """
        ids_in_rules = []
        for rule in self.json_rules:
            action = rule["action"]
            if "exceed_action_id" in action:
                ids_in_rules.append(action["exceed_action_id"])

        # we're only looking for matches, so strip duplicates and to make the comparison work
        return list(set(ids_in_rules))

    def test_exceed_action_ids_in_rules(self):
        """
        Tests that any exceed action id's under rules exist in exceed_actions (but not the other way around)
        """
        ids_in_rules = self.get_exceed_action_ids_in_quota_rules()

        # Remove empty ids, this is for the cases where we need to pickup default
        ids_in_rules = ' '.join(ids_in_rules).split()

        # ids in exceed actions are not a list, so grabbing them is easier. Strip duplicates like above.
        ids_in_exceed_actions = [exceed_action["id"] for exceed_action in self.json_exceed_actions]
        ids_in_exceed_actions = list(set(ids_in_exceed_actions))

        # check that all exceed action id's under rules are also under exceed_actions
        ids_contained = all(i in ids_in_exceed_actions for i in ids_in_rules)
        self.assertTrue(ids_contained, "Failed due to a mismatch in ids between rules and exceed actions.")

        # orphans the other way around are stored as warnings and printed later
        self.warnings_add_orphan(ids_in_exceed_actions, ids_in_rules, "exceed_actions")

    @classmethod
    def tearDownClass(cls):
        """
        Prints the orphan string.
        """
        print(cls.warning_dict)


if __name__ == '__main__':
    unittest.main()
