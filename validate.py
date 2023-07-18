#!/usr/bin/python3

import os
import json
import jsonschema
import sys

from  v1.policy_manager.validatepolicy import validate_policy

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
if json_data['policy_manager'] != None:
    validate_policy(json_data, schema_data)
