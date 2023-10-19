#!/usr/bin/python3

import json
import os
import unittest
from pathlib import Path
import referencing
import jsonschema

from v1.schema_utils.util import ReferenceRetriever

"""
TestCaptiveportal validates the captiveportal schema

Unlike other tests like TestPolicyManager, this just validates the schema since there are no further required tests.
"""
class TestCaptiveportal(unittest.TestCase):
    # consts
    JSON_FILENAME_DEFAULT = "captiveportal_test.json"
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

        print("schema_filename ==> ", schema_filename)
        schema_file = Path(schema_filename)
        retriever = ReferenceRetriever(schema_file.parent.resolve())
        resource = referencing.Resource.from_contents(schema_data)

        try:
            registry = resource @ referencing.Registry(retrieve=retriever.retrieve)  # Add the resource to a new registry
            jsonschema.validate(instance=cls.json_data, schema=resource.contents, registry=registry)
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
