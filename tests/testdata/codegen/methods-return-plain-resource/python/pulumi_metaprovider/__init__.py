# coding=utf-8
# *** WARNING: this file was generated by test. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import builtins as _builtins
from . import _utilities
import typing
# Export this package's modules as members:
from .configurer import *
from .provider import *
_utilities.register(
    resource_modules="""
[
 {
  "pkg": "metaprovider",
  "mod": "index",
  "fqn": "pulumi_metaprovider",
  "classes": {
   "metaprovider:index:Configurer": "Configurer"
  }
 }
]
""",
    resource_packages="""
[
 {
  "pkg": "metaprovider",
  "token": "pulumi:providers:metaprovider",
  "fqn": "pulumi_metaprovider",
  "class": "Provider"
 }
]
"""
)
