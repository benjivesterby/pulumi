# coding=utf-8
# *** WARNING: this file was generated by test. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import builtins as _builtins
import warnings
import sys
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict, TypeAlias
else:
    from typing_extensions import NotRequired, TypedDict, TypeAlias
from . import _utilities

__all__ = [
    'GetAmiIdsFilterArgs',
    'GetAmiIdsFilterArgsDict',
]

MYPY = False

if not MYPY:
    class GetAmiIdsFilterArgsDict(TypedDict):
        name: _builtins.str
        values: Sequence[_builtins.str]
elif False:
    GetAmiIdsFilterArgsDict: TypeAlias = Mapping[str, Any]

@pulumi.input_type
class GetAmiIdsFilterArgs:
    def __init__(__self__, *,
                 name: _builtins.str,
                 values: Sequence[_builtins.str]):
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "values", values)

    @_builtins.property
    @pulumi.getter
    def name(self) -> _builtins.str:
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: _builtins.str):
        pulumi.set(self, "name", value)

    @_builtins.property
    @pulumi.getter
    def values(self) -> Sequence[_builtins.str]:
        return pulumi.get(self, "values")

    @values.setter
    def values(self, value: Sequence[_builtins.str]):
        pulumi.set(self, "values", value)


