#!/usr/bin/python3

import os
import json
import jsonschema
import sys

def usage():
    """Print usage"""
    sys.stderr.write("""\
%s Usage:
  %s <schema_file> <json_file>
""" % (sys.argv[0],sys.argv[0]))
    exit(1)
    
if len(sys.argv) < 3:
    usage()

schema_filename = os.path.abspath(sys.argv[1])
json_filename = os.path.abspath(sys.argv[2])
(path, _) = os.path.split(schema_filename)
resolver = jsonschema.RefResolver('file://' + path + '/', None)

schema_file = open(schema_filename)
schema_data = json.load(schema_file)
schema_file.close()

json_file = open(json_filename)
json_data = json.load(json_file)
json_file.close()

jsonschema.validate(json_data, schema_data, resolver=resolver)

#Added some parsing for the policy_manager_schema
#This could be extened for any schema
if schema_filename.endswith("policy_manager_schema.json"):
    print('Parsing policy_manager data...')
    expected = {}
    for k in schema_data['definitions']['policy_manager_settings']['properties']:
        print('Expecting a key for', k)
        expected[k] = 0
    for entry in json_data['policy_manager']:
        if not entry in expected:
            print('Error: Found unexpected entry', entry)
        else:
            expected[entry] += 1
    for k in expected:
        v = expected[k]
        if v == 0:
            print('Error: Did not find definition of', k)
        elif v > 1:
            print('Error: Found duplicate entry for', k)
        else:
            print('Found expected entry', k)