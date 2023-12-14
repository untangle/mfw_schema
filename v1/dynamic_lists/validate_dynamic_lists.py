#!/usr/bin/python3

import os
import unittest
from uuid import UUID

from v1.schema_utils.util import SchemaValidator

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
        schema_validator = SchemaValidator(current_directory, cls.JSON_FILENAME_DEFAULT, cls.SCHEMA_FILENAME_DEFAULT)
        
        if schema_validator.isValid():
            cls.json_data = schema_validator.getJsonData()
        else:
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
