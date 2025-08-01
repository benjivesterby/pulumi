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
import pulumi_tls

__all__ = ['ConfigurerArgs', 'Configurer']

@pulumi.input_type
class ConfigurerArgs:
    def __init__(__self__, *,
                 tls_proxy: Optional[pulumi.Input[_builtins.str]] = None):
        """
        The set of arguments for constructing a Configurer resource.
        """
        if tls_proxy is not None:
            pulumi.set(__self__, "tls_proxy", tls_proxy)

    @_builtins.property
    @pulumi.getter(name="tlsProxy")
    def tls_proxy(self) -> Optional[pulumi.Input[_builtins.str]]:
        return pulumi.get(self, "tls_proxy")

    @tls_proxy.setter
    def tls_proxy(self, value: Optional[pulumi.Input[_builtins.str]]):
        pulumi.set(self, "tls_proxy", value)


@pulumi.type_token("metaprovider:index:Configurer")
class Configurer(pulumi.ComponentResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 tls_proxy: Optional[pulumi.Input[_builtins.str]] = None,
                 __props__=None):
        """
        Create a Configurer resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[ConfigurerArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Create a Configurer resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param ConfigurerArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConfigurerArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 tls_proxy: Optional[pulumi.Input[_builtins.str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is not None:
            raise ValueError('ComponentResource classes do not support opts.id')
        else:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ConfigurerArgs.__new__(ConfigurerArgs)

            __props__.__dict__["tls_proxy"] = tls_proxy
        super(Configurer, __self__).__init__(
            'metaprovider:index:Configurer',
            resource_name,
            __props__,
            opts,
            remote=True)

    @pulumi.output_type
    class MeaningOfLifeResult:
        def __init__(__self__, res=None):
            if res and not isinstance(res, int):
                raise TypeError("Expected argument 'res' to be a int")
            pulumi.set(__self__, "res", res)

        @_builtins.property
        @pulumi.getter
        def res(self) -> _builtins.int:
            return pulumi.get(self, "res")

    def meaning_of_life(__self__) -> int:
        __args__ = dict()
        __args__['__self__'] = __self__
        return _utilities.call_plain('metaprovider:index:Configurer/meaningOfLife', __args__, res=__self__, typ=Configurer.MeaningOfLifeResult).res

    @pulumi.output_type
    class ObjectMixResult:
        def __init__(__self__, meaning_of_life=None, provider=None):
            if meaning_of_life and not isinstance(meaning_of_life, int):
                raise TypeError("Expected argument 'meaning_of_life' to be a int")
            pulumi.set(__self__, "meaning_of_life", meaning_of_life)
            if provider and not isinstance(provider, pulumi_tls.Provider):
                raise TypeError("Expected argument 'provider' to be a pulumi_tls.Provider")
            pulumi.set(__self__, "provider", provider)

        @_builtins.property
        @pulumi.getter(name="meaningOfLife")
        def meaning_of_life(self) -> Optional[_builtins.int]:
            return pulumi.get(self, "meaning_of_life")

        @_builtins.property
        @pulumi.getter
        def provider(self) -> Optional['pulumi_tls.Provider']:
            return pulumi.get(self, "provider")

    def object_mix(__self__) -> ObjectMixResult:
        __args__ = dict()
        __args__['__self__'] = __self__
        return _utilities.call_plain('metaprovider:index:Configurer/objectMix', __args__, res=__self__, typ=Configurer.ObjectMixResult)

    @pulumi.output_type
    class TlsProviderResult:
        def __init__(__self__, res=None):
            if res and not isinstance(res, pulumi_tls.Provider):
                raise TypeError("Expected argument 'res' to be a pulumi_tls.Provider")
            pulumi.set(__self__, "res", res)

        @_builtins.property
        @pulumi.getter
        def res(self) -> 'pulumi_tls.Provider':
            return pulumi.get(self, "res")

    def tls_provider(__self__) -> pulumi_tls.Provider:
        __args__ = dict()
        __args__['__self__'] = __self__
        return _utilities.call_plain('metaprovider:index:Configurer/tlsProvider', __args__, res=__self__, typ=Configurer.TlsProviderResult).res

