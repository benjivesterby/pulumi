# coding=utf-8
# *** WARNING: this file was generated by test. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import builtins as _builtins
from .. import _utilities
import typing

# Make subpackages available:
if typing.TYPE_CHECKING:
    import pulumi_myPkg.mymod.childa as __childa
    childa = __childa
    import pulumi_myPkg.mymod.childb as __childb
    childb = __childb
else:
    childa = _utilities.lazy_import('pulumi_myPkg.mymod.childa')
    childb = _utilities.lazy_import('pulumi_myPkg.mymod.childb')

