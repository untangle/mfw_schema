#!/usr/bin/python3

import os
import unittest

from v1.schema_utils.util import SchemaValidator


class TestFirewallSchema(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "test_firewall.json"
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

    def test_dummy(self):
        """
        Dummy test, just enabling validation.
        
        TODO delete me if testing goes beyond validation
        """
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
    