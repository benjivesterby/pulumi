# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pulumi/codegen/mapper.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1bpulumi/codegen/mapper.proto\x12\x07\x63odegen\"\x82\x01\n\x11GetMappingRequest\x12\x10\n\x08provider\x18\x01 \x01(\t\x12\x17\n\x0fpulumi_provider\x18\x02 \x01(\t\x12\x42\n\x15parameterization_hint\x18\x03 \x01(\x0b\x32#.codegen.MapperParameterizationHint\"J\n\x1aMapperParameterizationHint\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\x0c\"\"\n\x12GetMappingResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\x32Q\n\x06Mapper\x12G\n\nGetMapping\x12\x1a.codegen.GetMappingRequest\x1a\x1b.codegen.GetMappingResponse\"\x00\x42\x32Z0github.com/pulumi/pulumi/sdk/v3/proto/go/codegenb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'pulumi.codegen.mapper_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z0github.com/pulumi/pulumi/sdk/v3/proto/go/codegen'
  _GETMAPPINGREQUEST._serialized_start=41
  _GETMAPPINGREQUEST._serialized_end=171
  _MAPPERPARAMETERIZATIONHINT._serialized_start=173
  _MAPPERPARAMETERIZATIONHINT._serialized_end=247
  _GETMAPPINGRESPONSE._serialized_start=249
  _GETMAPPINGRESPONSE._serialized_end=283
  _MAPPER._serialized_start=285
  _MAPPER._serialized_end=366
# @@protoc_insertion_point(module_scope)
