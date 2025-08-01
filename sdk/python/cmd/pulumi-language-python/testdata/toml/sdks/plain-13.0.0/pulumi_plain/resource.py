# coding=utf-8
# *** WARNING: this file was generated by pulumi-language-python. ***
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
from . import outputs
from ._inputs import *

__all__ = ['ResourceArgs', 'Resource']

@pulumi.input_type
class ResourceArgs:
    def __init__(__self__, *,
                 data: 'DataArgs',
                 non_plain_data: Optional[pulumi.Input['DataArgs']] = None):
        """
        The set of arguments for constructing a Resource resource.
        :param pulumi.Input['DataArgs'] non_plain_data: A non plain input to compare against the plain inputs, as well as testing plain/non-plain nesting.
        """
        pulumi.set(__self__, "data", data)
        if non_plain_data is not None:
            pulumi.set(__self__, "non_plain_data", non_plain_data)

    @_builtins.property
    @pulumi.getter
    def data(self) -> 'DataArgs':
        return pulumi.get(self, "data")

    @data.setter
    def data(self, value: 'DataArgs'):
        pulumi.set(self, "data", value)

    @_builtins.property
    @pulumi.getter(name="nonPlainData")
    def non_plain_data(self) -> Optional[pulumi.Input['DataArgs']]:
        """
        A non plain input to compare against the plain inputs, as well as testing plain/non-plain nesting.
        """
        return pulumi.get(self, "non_plain_data")

    @non_plain_data.setter
    def non_plain_data(self, value: Optional[pulumi.Input['DataArgs']]):
        pulumi.set(self, "non_plain_data", value)


@pulumi.type_token("plain:index:Resource")
class Resource(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data: Optional[Union['DataArgs', 'DataArgsDict']] = None,
                 non_plain_data: Optional[pulumi.Input[Union['DataArgs', 'DataArgsDict']]] = None,
                 __props__=None):
        """
        Create a Resource resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Union['DataArgs', 'DataArgsDict']] non_plain_data: A non plain input to compare against the plain inputs, as well as testing plain/non-plain nesting.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ResourceArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Create a Resource resource with the given unique name, props, and options.
        :param str resource_name: The name of the resource.
        :param ResourceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ResourceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 data: Optional[Union['DataArgs', 'DataArgsDict']] = None,
                 non_plain_data: Optional[pulumi.Input[Union['DataArgs', 'DataArgsDict']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ResourceArgs.__new__(ResourceArgs)

            if data is None and not opts.urn:
                raise TypeError("Missing required property 'data'")
            __props__.__dict__["data"] = data
            __props__.__dict__["non_plain_data"] = non_plain_data
        super(Resource, __self__).__init__(
            'plain:index:Resource',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None) -> 'Resource':
        """
        Get an existing Resource resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = ResourceArgs.__new__(ResourceArgs)

        __props__.__dict__["data"] = None
        __props__.__dict__["non_plain_data"] = None
        return Resource(resource_name, opts=opts, __props__=__props__)

    @_builtins.property
    @pulumi.getter
    def data(self) -> pulumi.Output['outputs.Data']:
        return pulumi.get(self, "data")

    @_builtins.property
    @pulumi.getter(name="nonPlainData")
    def non_plain_data(self) -> pulumi.Output[Optional['outputs.Data']]:
        """
        A non plain input to compare against the plain inputs, as well as testing plain/non-plain nesting.
        """
        return pulumi.get(self, "non_plain_data")

