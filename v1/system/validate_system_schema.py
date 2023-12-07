#!/usr/bin/python3

import os
import unittest

from v1.schema_utils.util import SchemaValidator


class TestSystemSchema(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "test_system_schema.json"
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

    def test_system_logging(self):
        """
        validates system logging
        """
        system_logging = self.json_data["system"]["logging"]
        self.assertTrue(system_logging["type"] in ["file", "circular"], "Failed due to the invalid logging type")
        self.assertTrue(system_logging["protocol"] in ["tcp", "udp"], "Failed due to the invalid logging protocol value")
        if system_logging["remote"]:
            self.assertTrue(system_logging.get("ip", False), "Failed due to the absence of a 'ip' field value")
            self.assertTrue(system_logging.get("port", False), "Failed due to the absence of a 'port' field value")

    def test_system(self):
        """
        validates system
        """
        system = self.json_data["system"]
        self.assertTrue(system.get("hostName", False),  "Failed due to the absence of a 'hostName' field value")
        self.assertTrue(system.get("domainName", False), "Failed due to the absence of a 'domainName' field value")

if __name__ == '__main__':
    unittest.main()
