#!/usr/bin/python3

import argparse
import os
import unittest
import sys

import v1.policy_manager.validatepolicy as validatepolicy
import v1.dynamic_lists.validate_dynamic_lists as validate_dynamic_lists
import v1.captiveportal.validate_captiveportal as validate_captiveportal
import v1.system.validate_system_schema as validate_system_schema
import v1.webroot.validate_webroot_schema as webroot_system_schema

validate_dict = {
    "dynamic_lists": validate_dynamic_lists,
    "policy_manager": validatepolicy,
    "captiveportal": validate_captiveportal,
    "system_schema": validate_system_schema,
    "webroot_schema": webroot_system_schema
}

def main():
    """
    Grabs passed arguments, and then uses that information to validate a json file against a schema. Usage:
        > validate.py schema_file json_file
    """
    parser = argparse.ArgumentParser(description=__file__ + " Usage:")
    parser.add_argument("directories", type=str, nargs='?', default="", help="directories whose schema will be validated. For multiple, separate with a comma")
    parser.add_argument("schema_file", type=str, nargs='?', default="", help="The schema to validate against. Blank uses directory default.")
    parser.add_argument("json_file", type=str, nargs='?', default="", help="The json file to validate. Blank uses directory default.")
    args = parser.parse_args()
    
    os.environ["SCHEMA_FILE"] = args.schema_file
    os.environ["JSON_FILE"]   = args.json_file
    directories = args.directories.split(",") if len(args.directories) > 0 else list(validate_dict.keys())
    for directory in directories:
        run_test_on_module(validate_dict[directory])
    os.environ.pop("SCHEMA_FILE", None)
    os.environ.pop("JSON_FILE", None)
    
def run_test_on_module(module):
    print("=== START OF MODULE TEST: " + str(module) + " ===\n")
    # Sets environment variables with the passed files, runs validation, then deletes as a teardown
    suite = unittest.TestLoader().loadTestsFromModule(module)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print("=== END OF MODULE TEST: " + str(module) + " ===\n")

if __name__ == '__main__':
    main()