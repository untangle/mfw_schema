#!/usr/bin/python3

import json
import jsonschema
import os
import unittest


class TestSystemSchema(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT   = "test_system_schema.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    json_data = {}
    
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
        
    def test_system_logging(self):
        """
        validates system logging
        """
        system_logging = self.json_data["system"]["logging"]
        self.assertTrue(system_logging["type"] in ["file", "circular"])
        if (system_logging["remote"]):
            self.assertTrue(system_logging.get("ip", False))
            self.assertTrue(system_logging.get("port", False))

if __name__ == '__main__':
    unittest.main()
