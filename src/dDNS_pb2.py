# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: dDNS.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ndDNS.proto\"\x10\n\x02ID\x12\n\n\x02id\x18\x01 \x01(\x05\"$\n\x07\x46ORDATA\x12\r\n\x05preId\x18\x01 \x01(\x05\x12\n\n\x02id\x18\x02 \x01(\x05\".\n\x04\x44\x41TA\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\x12\n\n\x02ip\x18\x02 \x01(\t\x12\n\n\x02id\x18\x03 \x01(\x05\"!\n\x07\x44\x41TASET\x12\x16\n\x07\x64\x61taset\x18\x01 \x03(\x0b\x32\x05.DATA\"\x14\n\x04NULL\x12\x0c\n\x04null\x18\x01 \x01(\x05\"\x16\n\x05TOPRE\x12\r\n\x05mysuc\x18\x01 \x01(\x05\".\n\x05TOSUC\x12\r\n\x05mypre\x18\x01 \x01(\x05\x12\x16\n\x07\x64\x61taset\x18\x02 \x03(\x0b\x32\x05.DATA\"!\n\x03\x41\x44\x44\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\x12\n\n\x02ip\x18\x02 \x01(\t\"\x15\n\x03\x44\x45L\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\"=\n\x06MODIFY\x12\x11\n\toldDomain\x18\x01 \x01(\t\x12\x11\n\tnewDomain\x18\x03 \x01(\t\x12\r\n\x05newIp\x18\x04 \x01(\t\"\x17\n\x05QUERY\x12\x0e\n\x06\x64omain\x18\x01 \x01(\t\"%\n\x04RESP\x12\x0b\n\x03\x65rr\x18\x01 \x01(\x08\x12\x10\n\x08response\x18\x02 \x01(\t2\xe0\x01\n\nrpcService\x12\x0f\n\x03\x41sk\x12\x03.ID\x1a\x03.ID\x12 \n\nAskForData\x12\x08.FORDATA\x1a\x08.DATASET\x12\x16\n\x05ToPre\x12\x06.TOPRE\x1a\x05.NULL\x12\x16\n\x05ToSuc\x12\x06.TOSUC\x1a\x05.NULL\x12\x12\n\x04Quit\x12\x03.ID\x1a\x05.NULL\x12\x12\n\x03\x41\x64\x64\x12\x04.ADD\x1a\x05.RESP\x12\x15\n\x06Remove\x12\x04.DEL\x1a\x05.RESP\x12\x18\n\x06Modify\x12\x07.MODIFY\x1a\x05.RESP\x12\x16\n\x05Query\x12\x06.QUERY\x1a\x05.RESPb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'dDNS_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ID']._serialized_start=14
  _globals['_ID']._serialized_end=30
  _globals['_FORDATA']._serialized_start=32
  _globals['_FORDATA']._serialized_end=68
  _globals['_DATA']._serialized_start=70
  _globals['_DATA']._serialized_end=116
  _globals['_DATASET']._serialized_start=118
  _globals['_DATASET']._serialized_end=151
  _globals['_NULL']._serialized_start=153
  _globals['_NULL']._serialized_end=173
  _globals['_TOPRE']._serialized_start=175
  _globals['_TOPRE']._serialized_end=197
  _globals['_TOSUC']._serialized_start=199
  _globals['_TOSUC']._serialized_end=245
  _globals['_ADD']._serialized_start=247
  _globals['_ADD']._serialized_end=280
  _globals['_DEL']._serialized_start=282
  _globals['_DEL']._serialized_end=303
  _globals['_MODIFY']._serialized_start=305
  _globals['_MODIFY']._serialized_end=366
  _globals['_QUERY']._serialized_start=368
  _globals['_QUERY']._serialized_end=391
  _globals['_RESP']._serialized_start=393
  _globals['_RESP']._serialized_end=430
  _globals['_RPCSERVICE']._serialized_start=433
  _globals['_RPCSERVICE']._serialized_end=657
# @@protoc_insertion_point(module_scope)
