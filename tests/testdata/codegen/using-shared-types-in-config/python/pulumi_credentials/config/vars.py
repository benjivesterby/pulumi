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
from .. import _utilities
from .. import _enums as _root_enums
from .. import outputs as _root_outputs

import types

__config__ = pulumi.Config('credentials')


class _ExportableConfig(types.ModuleType):
    @_builtins.property
    def hash(self) -> Optional[str]:
        """
        The (entirely uncryptographic) hash function used to encode the "password".
        """
        return __config__.get('hash')

    @_builtins.property
    def password(self) -> str:
        """
        The password. It is very secret.
        """
        return __config__.get('password') or (_utilities.get_env('FOO') or '')

    @_builtins.property
    def shared(self) -> Optional[str]:
        return __config__.get('shared')

    @_builtins.property
    def user(self) -> Optional[str]:
        """
        The username. Its important but not secret.
        """
        return __config__.get('user')

