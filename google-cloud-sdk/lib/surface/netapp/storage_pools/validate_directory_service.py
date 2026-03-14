# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Validate directory service for a Cloud Netapp storage pool."""

from googlecloudsdk.api_lib.netapp.storage_pools import client as storagepools_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.storage_pools import flags as storagepools_flags


def _CommonArgs(parser):
  storagepools_flags.AddStoragePoolValidateDirectoryServiceArg(parser)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class ValidateDirectoryService(base.Command):
  """Validate directory service for a Cloud Netapp storage pool."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Validate the directory service for a Cloud Netapp storage pool.
          """,
      'EXAMPLES': """\
          The following command validates the directory service of type ACTIVE_DIRECTORY for a storage pool named NAME:

              $ {command} NAME --location=us-central1 --directory-service-type=ACTIVE_DIRECTORY

          """,
  }

  @staticmethod
  def Args(parser):
    _CommonArgs(parser)

  def Run(self, args):
    """Validate directory service for a Cloud Netapp storage pool."""
    storagepool_ref = args.CONCEPTS.storage_pool.Parse()
    client = storagepools_client.StoragePoolsClient(self._RELEASE_TRACK)
    directory_service_type_enum = (
        storagepools_flags.GetDirectoryServiceTypeEnumFromArg(
            args.directory_service_type, client.messages
        )
    )
    result = client.ValidateDirectoryService(
        storagepool_ref,
        directory_service_type_enum,
        args.async_,
    )
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ValidateDirectoryServiceBeta(ValidateDirectoryService):
  """Validate directory service for a Cloud Netapp storage pool."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
