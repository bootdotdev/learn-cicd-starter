# -*- coding: utf-8 -*- #
# Copyright 2022 Google LLC. All Rights Reserved.
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
"""Updates a Cloud NetApp Storage Pool."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.netapp.storage_pools import client as storagepools_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.storage_pools import flags as storagepools_flags
from googlecloudsdk.command_lib.util.args import labels_util

from googlecloudsdk.core import log


def _CommonArgs(parser, release_track):
  storagepools_flags.AddStoragePoolUpdateArgs(parser, release_track)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update a Cloud NetApp Storage Pool."""

  _RELEASE_TRACK = base.ReleaseTrack.GA

  detailed_help = {
      'DESCRIPTION': """\
          Updates a Storage Pool with given arguments
          """,
      'EXAMPLES': """\
          The following command updates a Storage Pool named NAME in the given location

              $ {command} NAME --location=us-central1 --capacity=4096 --active-directory=ad-2 --description="new description" --update-labels=key1=val1
          """,
  }

  @staticmethod
  def Args(parser):
    _CommonArgs(parser, Update._RELEASE_TRACK)

  def Run(self, args):
    """Update a Cloud NetApp Storage Pool in the current project."""
    storagepool_ref = args.CONCEPTS.storage_pool.Parse()
    client = storagepools_client.StoragePoolsClient(self._RELEASE_TRACK)
    labels_diff = labels_util.Diff.FromUpdateArgs(args)
    orig_storagepool = client.GetStoragePool(storagepool_ref)
    capacity_in_gib = args.capacity >> 30 if args.capacity else None
    ## Update labels
    if labels_diff.MayHaveUpdates():
      labels = labels_diff.Apply(
          client.messages.StoragePool.LabelsValue, orig_storagepool.labels
      ).GetOrNone()
    else:
      labels = None

    zone = args.zone
    replica_zone = args.replica_zone
    if args.total_throughput is not None:
      total_throughput_mibps = args.total_throughput >> 20
    else:
      total_throughput_mibps = None
    hot_tier_size_gib = None
    enable_hot_tier_auto_resize = None
    qos_type = None
    if args.qos_type is not None:
      qos_type = storagepools_flags.GetStoragePoolQosTypeArg(
          client.messages
      ).GetEnumForChoice(args.qos_type)
    if (self._RELEASE_TRACK == base.ReleaseTrack.ALPHA or
        self._RELEASE_TRACK == base.ReleaseTrack.BETA):
      if args.hot_tier_size is not None:
        hot_tier_size_gib = args.hot_tier_size >> 30
      enable_hot_tier_auto_resize = args.enable_hot_tier_auto_resize

    storage_pool = client.ParseUpdatedStoragePoolConfig(
        orig_storagepool,
        capacity=capacity_in_gib,
        active_directory=args.active_directory,
        description=args.description,
        labels=labels,
        allow_auto_tiering=args.allow_auto_tiering,
        zone=zone,
        replica_zone=replica_zone,
        total_throughput=total_throughput_mibps,
        total_iops=args.total_iops,
        hot_tier_size=hot_tier_size_gib,
        enable_hot_tier_auto_resize=enable_hot_tier_auto_resize,
        qos_type=qos_type,
    )

    updated_fields = []
    if args.IsSpecified('capacity'):
      updated_fields.append('capacityGib')
    if args.IsSpecified('active_directory'):
      updated_fields.append('activeDirectory')
    if args.IsSpecified('description'):
      updated_fields.append('description')
    if (
        args.IsSpecified('update_labels')
        or args.IsSpecified('remove_labels')
        or args.IsSpecified('clear_labels')
    ):
      updated_fields.append('labels')
    if args.IsSpecified('allow_auto_tiering'):
      updated_fields.append('allowAutoTiering')
    if args.IsSpecified('zone'):
      updated_fields.append('zone')
    if args.IsSpecified('replica_zone'):
      updated_fields.append('replicaZone')
    if args.IsSpecified('total_throughput'):
      updated_fields.append('totalThroughputMibps')
    if args.IsSpecified('total_iops'):
      updated_fields.append('totalIops')
    if args.IsSpecified('qos_type'):
      updated_fields.append('qosType')
    if (self._RELEASE_TRACK == base.ReleaseTrack.ALPHA or
        self._RELEASE_TRACK == base.ReleaseTrack.BETA):
      if args.IsSpecified('hot_tier_size'):
        updated_fields.append('hotTierSizeGib')
      if args.IsSpecified('enable_hot_tier_auto_resize'):
        updated_fields.append('enableHotTierAutoResize')

    update_mask = ','.join(updated_fields)

    result = client.UpdateStoragePool(
        storagepool_ref, storage_pool, update_mask, args.async_
    )
    if args.async_:
      command = 'gcloud {} netapp storage-pools list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the updated storage pool by listing all storage'
          ' pools:\n  $ {} '.format(command)
      )
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update a Cloud NetApp Storage Pool."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA

  @staticmethod
  def Args(parser):
    _CommonArgs(parser, UpdateBeta._RELEASE_TRACK)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateBeta):
  """Update a Cloud NetApp Storage Pool."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA

  @staticmethod
  def Args(parser):
    _CommonArgs(parser, UpdateAlpha._RELEASE_TRACK)
