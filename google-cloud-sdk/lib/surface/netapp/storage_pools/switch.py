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
"""Switch a Regional Cloud NetApp Flex Storage Pool zone."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.storage_pools import client as storagepools_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.storage_pools import flags as storagepools_flags
from googlecloudsdk.core import log


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA
)
class Switch(base.Command):
  """Switch a Regional Cloud NetApp Flex Storage Pool zone."""

  detailed_help = {
      'DESCRIPTION': """\
          Switch a Regional Cloud NetApp Flex Storage Pool zone.
          """,
      'EXAMPLES': """\
          The following command switches zone of a Storage Pool named NAME using the required arguments:

              $ {command} NAME --location=us-central1

          To switch zone of a Storage Pool named NAME asynchronously, run the following command:

              $ {command} NAME --location=us-central1 --async
          """,
  }

  @staticmethod
  def Args(parser):
    storagepools_flags.AddStoragePoolSwitchArg(parser)

  def Run(self, args):
    """Switch a Regional Cloud NetApp Flex Storage Pool zone in the current project."""
    storagepool_ref = args.CONCEPTS.storage_pool.Parse()

    client = storagepools_client.StoragePoolsClient(self.ReleaseTrack())
    result = client.SwitchStoragePool(storagepool_ref, args.async_)
    if args.async_:
      command = 'gcloud {} netapp storage-pools list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the zone switch of storage pool by listing all'
          ' storage pools:\n  $ {} '.format(command)
      )
    return result
