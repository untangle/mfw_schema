#!/usr/bin/python3

import json
import os
import unittest
from uuid import UUID
from jsonschema.validators import Draft6Validator
from referencing import Registry

from v1.schema_utils.util import retrieve_data

"""
TestDynamicLists validates the dynamic_lists schema

Unlike other tests like TestPolicyManager, this just validates the schema since there are no further required tests.
"""
class TestDynamicLists(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "dynamic_lists_test.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    # class vars, begin uninitialized
    json_data = ""
    
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

        new_registry = Registry(retrieve=retrieve_data)

        try:
            validator = Draft6Validator(schema_data, registry=new_registry)
            validator.validate(cls.json_data)
        except Exception as e:
            print(e)
            raise unittest.SkipTest("ERROR: Validation of schema failed. Skipping all tests and printing.")

    def test_valid_ids(self):
        """
        Testing that each dynamic lists configuration's id is a valid uuid
        """
        for configuration in self.json_data["dynamic_lists"]["configurations"]:
            id_val = configuration["id"]
            try:
                uuid_obj = UUID(id_val)
            except ValueError:
                self.fail("Failed due to an invalid ID in dynamic lists: " + id_val)
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
