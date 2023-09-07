#!/usr/bin/python3

import argparse
import os
import unittest
import sys

import v1.policy_manager.validatepolicy as validatepolicy
import v1.dynamic_lists.validate_dynamic_lists as validate_dynamic_lists

def main():
    """
    Grabs passed arguments, and then uses that information to validate a json file against a schema. Usage:
        > validate.py schema_file json_file
    """
    parser = argparse.ArgumentParser(description=__file__ + " Usage:")
    parser.add_argument("schema_file", type=str, help="The schema to validate against")
    parser.add_argument("json_file", type=str, help="The json file to validate")
    # Print help message if no args are passed
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    
    # Sets environment variables with the passed files, runs validation, then deletes as a teardown
    os.environ["SCHEMA_FILE"] = args.schema_file
    os.environ["JSON_FILE"]   = args.json_file
    suite = unittest.TestLoader().loadTestsFromModule(validatepolicy)
    unittest.TextTestRunner(verbosity=2).run(suite)
    os.environ.pop("SCHEMA_FILE", None)
    os.environ.pop("JSON_FILE", None)
    
    # NOTE: this runs, but will throw a warning. Just a quick fix, but in the future the agrument variable structure
    # will need to accomodate more than just policy_manager
    suite = unittest.TestLoader().loadTestsFromModule(validate_dynamic_lists)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()