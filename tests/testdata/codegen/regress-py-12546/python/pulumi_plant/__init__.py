# coding=utf-8
# *** WARNING: this file was generated by test. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import builtins as _builtins
from . import _utilities
import typing
# Export this package's modules as members:
from ._enums import *
from .provider import *
from ._inputs import *
from . import outputs

# Make subpackages available:
if typing.TYPE_CHECKING:
    import pulumi_plant.tree as __tree
    tree = __tree
else:
    tree = _utilities.lazy_import('pulumi_plant.tree')

_utilities.register(
    resource_modules="""
[
 {
  "pkg": "plant",
  "mod": "tree/v1",
  "fqn": "pulumi_plant.tree.v1",
  "classes": {
   "plant:tree/v1:RubberTree": "RubberTree"
  }
 }
]
""",
    resource_packages="""
[
 {
  "pkg": "plant",
  "token": "pulumi:providers:plant",
  "fqn": "pulumi_plant",
  "class": "Provider"
 }
]
"""
)
