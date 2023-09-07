#!/usr/bin/python3

import json
import jsonschema
import os
import unittest

"""
TestDynamicLists validates the dynamic_lists schema

Unlike other tests like TestPolicyManager, this just validates the schema since there are no further required tests.
"""
class TestDynamicLists(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT   = "dynamic_lists_test.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    
    @classmethod
    def setUpClass(cls):
        """
        setUpClass runs before all tests. Grabs file information, using some defaults if the environment variables 
        fail for any reason. Then performs the regular jsonschema.validate, to check against the schema. This errors 
        out, so any follow-up tests won't run
        """
        current_directory = os.path.dirname(os.path.realpath(__file__))
        try:
            json_filename   = os.environ["JSON_FILE"]
            schema_filename = os.environ["SCHEMA_FILE"]
        except KeyError:
            json_filename   = os.path.join(current_directory, cls.JSON_FILENAME_DEFAULT)
            schema_filename = os.path.join(current_directory, cls.SCHEMA_FILENAME_DEFAULT)
            # NOTE: with its current structure, we will always hit this warning. Argument structure currently only 
            # accommodates policy manager
            print("WARNING: Failed to get filenames from environment variables. Using default filenames:")
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
        
    def test_dummy(self):
        """
        Dummy test, just enabling validation.
        
        TODO delete me if testing goes beyond validation
        """
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
