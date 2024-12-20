# Copyright 2016-2024, Pulumi Corporation.  All rights reserved.

import binascii
import os
from pulumi import export
from pulumi.dynamic import Resource, ResourceProvider, CreateResult

class RandomResourceProvider(ResourceProvider):
    serialize_as_secret_always = False

    def create(self, props):
        val = binascii.b2a_hex(os.urandom(15)).decode("ascii")
        return CreateResult(val, { "val": val })

class Random(Resource):
    val: str
    def __init__(self, name, opts = None):
        super().__init__(RandomResourceProvider(), name, {"val": ""}, opts)

r = Random("foo")

export("random_id", r.id)
export("random_val", r.val)
