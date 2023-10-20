#!/usr/bin/python3

import json
import pathlib
import referencing
from urllib.parse import urlparse

class ReferenceRetriever:
    def __init__(self, root_path):
        self.root_path = root_path

    def retrieve(self, uri):
        parsed_uri = urlparse(uri)
        p = pathlib.Path(parsed_uri.path).relative_to("/")
        with open(self.root_path / p) as f:
            return referencing.Resource.from_contents(json.load(f))
