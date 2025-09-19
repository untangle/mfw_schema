#!/usr/bin/python3

import json
import os
import pathlib
import jsonschema
import referencing
from urllib.parse import urlparse
from pathlib import Path
from jsonschema import validators


def properties_greater_than(validator, properties, instance, schema):
    if not isinstance(instance, dict):
        return

    greater_property = properties.get("greater")
    lesser_property = properties.get("lesser")

    if not greater_property or not lesser_property:
        return

    if greater_property in instance and lesser_property in instance:
        if instance[greater_property] <= instance[lesser_property]:
            yield jsonschema.ValidationError(
                f"'{greater_property}' must be greater than '{lesser_property}'"
            )


def extend_with_custom_validation(validator_class):
    validate_properties = validator_class.VALIDATORS.copy()
    validate_properties["propertiesGreaterThan"] = properties_greater_than
    return validators.extend(validator_class, validate_properties)


CustomDraft6Validator = extend_with_custom_validation(jsonschema.Draft6Validator)


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
    external_refs = {}

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
            for path in self.external_refs:
                registry = self.__importExternalRef(registry, path, self.external_refs[path])
            
            jsonschema.validate(instance=self.json_data, schema=resource.contents, registry=registry, cls=CustomDraft6Validator)
        except Exception as e:
            print(e)
            return False

        return True

    def addExternalRef(self, path, ref):
        self.external_refs[path] = ref

    def getJsonData(self):
        return self.json_data

    def __importExternalRef(self, registry: referencing.Registry, path: str, ref: str):
        schema_file_path = Path(path)
        schema_data = self.__readSchemaData(schema_file_path)
        schema_data["$id"] = schema_file_path.name
        registry = registry.with_resource(ref, referencing.Resource.from_contents(schema_data))
        
        return registry

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