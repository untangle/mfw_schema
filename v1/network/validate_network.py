#!/usr/bin/python3

import os
import unittest

from v1.schema_utils.util import SchemaValidator


class TestNetworkSchema(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "test_network.json"
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
        schema_validator = SchemaValidator(current_directory, cls.JSON_FILENAME_DEFAULT, cls.SCHEMA_FILENAME_DEFAULT)
        
        if schema_validator.isValid():
            cls.json_data = schema_validator.getJsonData()
        else:
            raise unittest.SkipTest("ERROR: Validation of schema failed. Skipping all tests and printing.")

    def test_network(self):
        """
        validates network
        """
        network = self.json_data["network"]
        self.assertEqual(len(network.get("devices")), 0,  "Invalid devices content")
        self.assertEqual(len(network.get("interfaces")), 1,  "Invalid interfaces content")
        self.assertEqual(len(network.get("switches")), 2,  "Invalid switches content")

if __name__ == '__main__':
    unittest.main()
    