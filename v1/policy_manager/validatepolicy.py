#!/usr/bin/python3

import os
import json
import jsonschema
import sys

# These functions will run if policy_manager data  is found in the json data on invocation of validate.py
# These are not strictly required but They supplement the validation done by the json parser by sanity 
# checking the internal cross-references based on id and checking for orphans.

ids = {}

def printCondition(prefix,c):
    """ Print a policy condition with indentation """
    errors = 0
    if c.get('value') is not None:
        print(prefix,'Condition:',c['type'], c['op'], c['value'])
    else:
        print(prefix,'Condition:',c['type'], c['op'], '\tGroup:', c['groupid'])
        groupid = c.get('groupid')
        if groupid is not None:
            group = groups[groupid]
            printGroup('\t'+prefix, group)
            group['ref'] = 1 + group['ref']
            items = group.get('items')
            errors += checkGroupItems('\t', group, items)
    return errors

# Used to keep track of individual configurations
configurations = {}

def checkConfiguration(prefix, c):
    """ Check a policy configuration with indentation """
    errors = 0
    if c.get('webfilter') is not None:
        webf = c['webfilter']
        print(prefix, 'Webfilter:\tEnabled:',webf['enabled'])
        if webf.get('blockList') is not None:
            print('\t'+prefix, 'BlockList', webf['blockList'])
        if webf.get('categories') is not None:
            print('\t'+prefix, 'Categories', webf['categories'])
        if webf.get('passList') is not None:
            print('\t'+prefix, 'PassList', webf['passList'])
    elif c.get('threatprevention') is not None:
        tp = c['threatprevention']
        print(prefix, 'Threatprevention:\tEnabled:', tp['enabled'],'\tRedirect:',tp['redirect'],'\tSensitivity:',tp['sensitivity'])
        if tp.get('passList') is not None:
            print('\t'+prefix, 'PassList', tp['passList'])
    elif c.get('discovery') is not None:
        disc = c['discovery']
        print(prefix, 'Discovery:',disc)
    elif c.get('geoip') is not None:
        geoip = c['geoip']
        print(prefix, 'Geoip:\tName:',c['name'],'\tDesc:',c['description'])
        print(prefix, geoip)
    elif c.get('shaping') is not None:
        shaping = c['shaping']
        print(prefix, "Shaping:\t", shaping)
    else:
        print(prefix, 'Error: Unkown configuration type:', c)
        errors += 1
    return errors

def printConfiguration(prefix, c):
    """ Print a policy condition with indentation """
    print(prefix,'Config:',c['id'], 'Name:', c['name'], 'Desc:', c['description'])

# Used to keep track of individual condition_objects
condition_objects = {}

def printConditionObject(prefix,condition_object):
    """ Print a policy condition_object with indentation """
    errors = 0
    print(prefix,'ConditionObject:', condition_object['id'], '\tName:,',condition_object['name'], '\tDescriptions:',condition_object['description'])
    for condition in condition_object['conditions']:
        errors += printCondition('\t'+prefix,condition)
    return errors

# User to keep track of individual groups
groups = {}

def printGroup(prefix, g):
    """ Print a group with indentation """

    print(prefix,'Group:', g['id'], '\tName:',g['name'], '\tItems:',g['items'])

def checkGroupItems(prefix, g, items):
    """ Check items in a group with indentation """
    errors = 0
    type = g['type']
    if items is None or len(items) == 0:
        print('\t'+prefix, "Error - Group with empty items list")
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
    else:
        print('\t'+prefix, 'Error - Unknown Group type', type)
        errors += 1
    return errors

def validate_policy(json_data, schema_data):
    """ Validate the overall policy configuration """
    errors = 0
    print('Parsing policy_manager data...')
    # Keep track of configurations indexed by id
    # and also keep track of whether each is referenced
    for c in json_data['policy_manager']['configurations']:
        configurations[c['id']]=c
        c['ref'] = 0
        if ids.get(c['id']) is None:
            ids[c['id']] = 1
        else:
            ids[c['id']] += 1

    # Keep track of condition_objects indexed by id
    # and also keep track of whether each is referenced
    for k in json_data['policy_manager']['condition_objects']:
        id = k['id']
        condition_objects[id]=k
        k['ref'] = 0
        if ids.get(id) is None:
            ids[id] = 1
        else:
            ids[id] += 1

    # Keep track of groups indexed by id
    # and also keep track of whether each is referenced
    for g in json_data['policy_manager']['groups']:
        id = g['id']
        groups[id]=g
        g['ref'] = 0
        if ids.get(id) is None:
            ids[id] = 1
        else:
            ids[id] += 1

    # Build a map of policies indexed by id
    policies = {}
    for p in json_data['policy_manager']['policies']:
        id = p['id']
        policies[id]=p
        if ids.get(id) is None:
            ids[id] = 1
        else:
            ids[id] += 1

    for p, policy in policies.items():
        print('Analyzing policy:', p, '\tName:', policy['name'], '\tDesc:', policy['description'], '\tEnabled:', policy['enabled'])
        if 'services' in policy:
            if policy.get('condition_object') is not None:
                topcoid = policy['condition_object']
                condition_object = condition_objects[topcoid]
                errors += printConditionObject('\t\t',condition_object)
                condition_object['ref'] = 1 + condition_object['ref']
            else:
                topcoid = None
            for service in policy['services']:
                print('\tService:')
                configid = service['configuration']
                config = configurations[configid]
                printConfiguration('\t\t',config)
                config['ref'] = 1 + config['ref']
                errors += checkConfiguration('\t\t', config)
                if service.get('condition_object') is not None:
                    coid = service['condition_object']
                    condition_object = condition_objects[coid]
                    errors += printConditionObject('\t\t',condition_object)
                    condition_object['ref'] = 1 + condition_object['ref']
        else:
                for configid in policy['configurations']:
                    config = configurations[configid]
                    printConfiguration('\t',config)
                    config['ref'] = 1 + config['ref']
                    errors += checkConfiguration('\t\t', config)
                for coid in policy['condition_objects']:
                    condition_object = condition_objects[coid]
                    errors += printConditionObject('\t',condition_object)
                    condition_object['ref'] = 1 + condition_object['ref']

    print('ConditionObjects:')
    foundOrphaned = False
    for f, condition_object in condition_objects.items():
        if condition_object['ref'] > 0:
            printConditionObject('\t',condition_object)
        else:
            foundOrphaned = True
    if foundOrphaned:
        print('Orphaned ConditionObjects:')
        for f, condition_object in condition_objects.items():
            if condition_object['ref'] == 0:
                printConditionObject('\t',condition_object)
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
    for id in ids:
        count = ids[id]
        if count>1:
            print('ID replicated: ', id, 'count:', count)
            errors += 1
    print('Found', errors,'errors')
