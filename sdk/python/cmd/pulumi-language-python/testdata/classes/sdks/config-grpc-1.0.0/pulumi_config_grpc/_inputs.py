# coding=utf-8
# *** WARNING: this file was generated by pulumi-language-python. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import builtins
import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'Tbool1',
    'Tbool1Args',
    'Tbool2',
    'Tbool2Args',
    'Tbool3',
    'Tbool3Args',
    'Tint1',
    'Tint1Args',
    'Tint2',
    'Tint2Args',
    'Tint3',
    'Tint3Args',
    'Tnum1',
    'Tnum1Args',
    'Tnum2',
    'Tnum2Args',
    'Tnum3',
    'Tnum3Args',
    'TsecretBool1',
    'TsecretBool1Args',
    'TsecretBool2',
    'TsecretBool2Args',
    'TsecretBool3',
    'TsecretBool3Args',
    'TsecretInt1',
    'TsecretInt1Args',
    'TsecretInt2',
    'TsecretInt2Args',
    'TsecretInt3',
    'TsecretInt3Args',
    'TsecretNum1',
    'TsecretNum1Args',
    'TsecretNum2',
    'TsecretNum2Args',
    'TsecretNum3',
    'TsecretNum3Args',
    'TsecretString1',
    'TsecretString1Args',
    'TsecretString2',
    'TsecretString2Args',
    'TsecretString3',
    'TsecretString3Args',
    'Tstring1',
    'Tstring1Args',
    'Tstring2',
    'Tstring2Args',
    'Tstring3',
    'Tstring3Args',
]

@pulumi.input_type
class Tbool1:
    def __init__(__self__, *,
                 x: Optional[builtins.bool] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tbool1Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.bool]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tbool2:
    def __init__(__self__, *,
                 x: Optional[builtins.bool] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tbool2Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.bool]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tbool3:
    def __init__(__self__, *,
                 x: Optional[builtins.bool] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tbool3Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.bool]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint1:
    def __init__(__self__, *,
                 x: Optional[builtins.int] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.int]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint1Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.int]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint2:
    def __init__(__self__, *,
                 x: Optional[builtins.int] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.int]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint2Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.int]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint3:
    def __init__(__self__, *,
                 x: Optional[builtins.int] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.int]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tint3Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.int]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum1:
    def __init__(__self__, *,
                 x: Optional[builtins.float] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.float]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum1Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.float]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum2:
    def __init__(__self__, *,
                 x: Optional[builtins.float] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.float]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum2Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.float]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum3:
    def __init__(__self__, *,
                 x: Optional[builtins.float] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.float]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tnum3Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.float]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class TsecretBool1:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.bool] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretBool1Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.bool]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretBool2:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.bool] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretBool2Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.bool]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretBool3:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.bool] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.bool]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.bool]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretBool3Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.bool]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.bool]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.bool]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt1:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.int] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.int]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt1Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.int]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt2:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.int] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.int]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt2Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.int]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt3:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.int] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.int]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.int]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretInt3Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.int]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.int]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.int]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum1:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.float] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.float]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum1Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.float]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum2:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.float] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.float]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum2Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.float]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum3:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.float] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.float]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.float]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretNum3Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.float]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.float]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.float]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString1:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.str] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.str]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString1Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.str]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString2:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.str] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.str]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString2Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.str]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString3:
    def __init__(__self__, *,
                 secret_x: Optional[builtins.str] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[builtins.str]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class TsecretString3Args:
    def __init__(__self__, *,
                 secret_x: Optional[pulumi.Input[builtins.str]] = None):
        if secret_x is not None:
            pulumi.set(__self__, "secret_x", secret_x)

    @property
    @pulumi.getter(name="secretX")
    def secret_x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "secret_x")

    @secret_x.setter
    def secret_x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "secret_x", value)


@pulumi.input_type
class Tstring1:
    def __init__(__self__, *,
                 x: Optional[builtins.str] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.str]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tstring1Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.str]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tstring2:
    def __init__(__self__, *,
                 x: Optional[builtins.str] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.str]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tstring2Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.str]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tstring3:
    def __init__(__self__, *,
                 x: Optional[builtins.str] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[builtins.str]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[builtins.str]):
        pulumi.set(self, "x", value)


@pulumi.input_type
class Tstring3Args:
    def __init__(__self__, *,
                 x: Optional[pulumi.Input[builtins.str]] = None):
        if x is not None:
            pulumi.set(__self__, "x", x)

    @property
    @pulumi.getter
    def x(self) -> Optional[pulumi.Input[builtins.str]]:
        return pulumi.get(self, "x")

    @x.setter
    def x(self, value: Optional[pulumi.Input[builtins.str]]):
        pulumi.set(self, "x", value)


