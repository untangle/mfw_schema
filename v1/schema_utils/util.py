#!/usr/bin/python3

import json
import os
import pathlib
import jsonschema
import referencing
from urllib.parse import urlparse
from pathlib import Path

class ReferenceRetriever:
    def __init__(self, root_path):
        self.root_path = root_path

    def retrieve(self, uri):
        parsed_uri = urlparse(uri)
        p = pathlib.Path(parsed_uri.path).relative_to("/")
        with open(self.root_path / p) as f:
            return referencing.Resource.from_contents(json.load(f))

class SchemaValidator:

    json_filename = ""
    json_data = {}
    schema_filename = ""
    schema_data = {}

    def __init__(self, current_directory, json_filename_default, schema_filename_default):
        self.json_filename = self.__getJsonFileName(current_directory, json_filename_default)
        self.json_data = self.__readJsonData(self.json_filename)
        self.schema_filename = self.__setSchemaFilenName(current_directory, schema_filename_default)
        self.schema_data = self.__readSchemaData(self.schema_filename)

    def isValid(self):
        schema_file = Path(self.schema_filename)
        retriever = ReferenceRetriever(schema_file.parent.resolve())
        resource = referencing.Resource.from_contents(self.schema_data)

        try:
            # Add the resource to a new registry
            registry = resource @ referencing.Registry(retrieve=retriever.retrieve)  
            jsonschema.validate(instance=self.json_data, schema=resource.contents, registry=registry)
        except Exception as e:
            print(e)
            return False

        return True

    def getJsonData(self):
        return self.json_data

    def __getJsonFileName(self, current_directory, json_filename_default):
        if "JSON_FILE" in os.environ and os.environ["JSON_FILE"] != "":
            json_filename = os.environ["JSON_FILE"]
        else:
            json_filename = os.path.join(current_directory, json_filename_default)
            print("WARNING: Using default json filename:" + str(json_filename))

        return json_filename

    def __readJsonData(self, json_filename):
        with open(json_filename, "r") as json_fp:
            json_data = json.load(json_fp)
            return json_data

    def __setSchemaFilenName(self, current_directory, schema_filename_default):
        if "SCHEMA_FILE" in os.environ and os.environ["SCHEMA_FILE"] != "":
            schema_filename = os.environ["SCHEMA_FILE"]
        else:
            schema_filename = os.path.join(current_directory, schema_filename_default)
            print("WARNING: Using default schema filename:" + str(schema_filename))

        return schema_filename

    def __readSchemaData(self, schema_filename):
        with open(schema_filename, "r") as schema_fp:
            schema_data = json.load(schema_fp)            
            return schema_data