# Copyright 2016-2023, Pulumi Corporation.  All rights reserved.

import pulumi


class FooResource(pulumi.ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("my:module:FooResource", name, None, opts)


class ComponentResource(pulumi.ComponentResource):
    def __init__(self, name, opts=None):
        super().__init__("my:module:ComponentResource", name, None, opts)
        FooResource("childrenamed", pulumi.ResourceOptions(
            parent=self,
            aliases=[pulumi.Alias(name="child")]
        ))


ComponentResource("comp")
