#!/usr/bin/python3

import os
import json
import jsonschema
import sys

def printCondition(prefix,c):
    errors = 0
    if c.get('value') != None:
        print(prefix,'Condition:',c['type'], c['op'], c['value'])
    else:
        print(prefix,'Condition:',c['type'], c['op'], '\tGroup:', c['groupid'])
        groupid = c.get('groupid')
        if groupid != None:
            group = groups[groupid]
            printGroup('\t'+prefix, group)
            group['ref'] = 1 + group['ref']
            items = group.get('items')
            errors += checkGroupItems('\t', group, items)
    return errors

configurations = {}

def checkConfiguration(prefix, c):
    errors = 0
    if None != c.get('webfilter'):
        webf = c['webfilter']
        print(prefix, 'Webfilter:\tEnabled:',webf['enabled'])
        if None != webf.get('blockList'):
            print('\t'+prefix, 'BlockList', webf['blockList'])
        if None != webf.get('categories'):
            print('\t'+prefix, 'Categories', webf['categories'])
        if None != webf.get('passList'):
            print('\t'+prefix, 'PassList', webf['passList'])
    elif None != c.get('threatprevention'):
        tp = c['threatprevention']
        print(prefix, 'Threatprevention:\tEnabled:', tp['enabled'],'\tRedirect:',tp['redirect'],'\tSensitivity:',tp['sensitivity'])
        if None != tp.get('passList'):
            print('\t'+prefix, 'PassList', tp['passList'])
    elif None != c.get('discovery'):
        disc = c['discovery']
        print(prefix, 'Discovery:',disc)
    elif None != c.get('geoip'):
        geoip = c['geoip']
        print(prefix, 'Geoip:\tName:',c['name'],'\tDesc:',c['description'])
        print(prefix, geoip)
    else:
        print(prefix, 'Error: Unkown configuration type:', c)
        errors += 1
    return errors

def printConfiguration(prefix, c):
    print(prefix,'Config:',c['id'], 'Name:', c['name'], 'Desc:', c['description'])

flows = {}

def printFlow(prefix,flow):
    errors = 0
    print(prefix,'Flow:', flow['id'], '\tName:,',flow['name'], '\tDescriptions:',flow['description'])
    for condition in flow['conditions']:
        errors += printCondition('\t'+prefix,condition)
    return errors

groups = {}

def printGroup(prefix, g):
    print(prefix,'Group:', g['id'], '\tName:',g['name'], '\tItems:',g['items'])

def checkGroupItems(prefix, g, items):
    errors = 0
    type = g['type']
    if items == None or len(items) == 0:
        print('\t'+prefix, "Error - Group wtih empty items list")
    elif type == 'GeoIPLocation':
        for i in items:
            if 2 != len(i):
                print('\t'+prefix, 'Error - GeoIPLocation with weird format', i, 'in group', g)
                errors += 1
    elif type == 'IPAddrList':
        # IP Addr List Validation
        print('IPAdrrList found - not validated')
    elif type == 'ServiceEndpoint':
        for i in items:
            for k,v in i.items():
                if k != "protocol" and k != "port":
                    print('\t'+prefix, 'Error - ServiceEndPoint ihad unexpected field', k, v, 'in group', g)    
                    errors += 1
    return errors

def validate_policy():
#Added some parsing for the policy_manager_schema
#This could be extened for any schema
    errors = 0
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

    for c in json_data['policy_manager']['configurations']:
        configurations[c['id']]=c
        c['ref'] = 0

    for k in json_data['policy_manager']['flows']:
        flows[k['id']]=k
        k['ref'] = 0

    for g in json_data['policy_manager']['groups']:
        groups[g['id']]=g
        g['ref'] = 0

    policies = {}
    for p in json_data['policy_manager']['policies']:
        policies[p['id']]=p
    for p, policy in policies.items():
        print('Analyzing policy:', p, '\tName:', policy['name'], '\tDesc:', policy['description'], '\tEnabled:', policy['enabled'])
        for configid in policy['configurations']:
            config = configurations[configid]
            printConfiguration('\t',config)
            config['ref'] = 1 + config['ref']
            errors += checkConfiguration('\t\t', config)
        for flowid in policy['flows']:
            flow = flows[flowid]
            errors += printFlow('\t',flow)
            flow['ref'] = 1 + flow['ref']

    print('Flows:')
    foundOrphaned = False
    for f, flow in flows.items():
        if flow['ref'] > 0:
            printFlow('\t',flow)
        else:
            foundOrphaned = True
    if foundOrphaned:
        print('Orphaned Flows:')
        for f, flow in flows.items():
            if flow['ref'] == 0:
                printFlow('\t',flow)
    print('Groups:')
    foundOrphaned = False
    for g, group in groups.items():
        if group['ref'] > 0:
            printGroup('\t',group)
        else:
            foundOrphaned = True
    if foundOrphaned:
        print('Orphaned Groups:')
        for g, group in groups.items():
            if group['ref'] == 0:
                printGroup('\t',group)
    print('Configurations:')
    foundOrphaned = False
    for c, config in configurations.items():
        if config['ref'] > 0:
            printConfiguration('\t', config)
        else:
            foundOrphaned = True
    if foundOrphaned:
        print('Orphaned Configurations:')
        for c, config in configurations.items():
            if config['ref'] == 0:
                printConfiguration('\t', config)
    print('Found', errors,'errors')

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
    validate_policy()
