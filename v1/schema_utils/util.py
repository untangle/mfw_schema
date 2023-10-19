#!/usr/bin/python3

import json
import os
import pathlib
import referencing
from urllib.parse import urlsplit, urlparse


def retrieve_data(uri):
    """
    Retrieve data from a specified URI and return it as a referencing.Resource object.
    This function processes the URI and retrieves data from it.
    It handles local file ('file' scheme) URIs.

    Args:
    uri: The URI specifying the location of the data to retrieve.

    Returns:
    referencing.Resource: A Resource object representing the retrieved data.
    """
    parsed = urlsplit(uri)
    module_name = str(uri).replace("file:./", "").replace("_schema.json", "")
    file_path = os.path.dirname(os.path.realpath(__file__))
    absolute_module_path = file_path.replace("schema_utils", module_name)

    absolute_schema_path = ""
    if parsed.scheme == "file":
        parsedpath = absolute_module_path + parsed.path[1::]
        absolute_schema_path = pathlib.Path(parsedpath)
    contents = json.loads(absolute_schema_path.read_text())
    return referencing.Resource.from_contents(contents)


class ReferenceRetriever:

    def __init__(self, root_path):
        self.root_path = root_path

    def retrieve(self, uri):
        parsed_uri = urlparse(uri)
        p = pathlib.Path(parsed_uri.path).relative_to("/")
        with open(self.root_path / p) as f:
            return referencing.Resource.from_contents(json.load(f))
