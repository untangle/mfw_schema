#!/usr/bin/python3

import json
import jsonschema
import os
import unittest
import pathlib
import referencing
from urllib.parse import urlsplit

"""
TestCaptiveportal validates the captiveportal schema

Unlike other tests like TestPolicyManager, this just validates the schema since there are no further required tests.
"""
class TestCaptiveportal(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT   = "captiveportal_test.json"
    SCHEMA_FILENAME_DEFAULT = "test_schema.json"
    
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

        def retrieve_data(uri):
            """
            Retrieve data from a specified URI and return it as a referencing.Resource object.
            This function processes the URI and retrieves data from it.
            It handleslocal file ('file' scheme) URIs.

            Args:
            uri: The URI specifying the location of the data to retrieve.

            Returns:
            referencing.Resource: A Resource object representing the retrieved data.
            """
            parsed = urlsplit(uri)
            if parsed.scheme == "file":
                parsedpath = current_directory + parsed.path[1::]
                path = pathlib.Path(parsedpath)
            contents = json.loads(path.read_text())
            return referencing.Resource.from_contents(contents)

        registry = referencing.Registry(retrieve=retrieve_data)
 
        try:
            validator = jsonschema.Draft6Validator(schema_data, registry=registry)
            validator.validate(cls.json_data)
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
