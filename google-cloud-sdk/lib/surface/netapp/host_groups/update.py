# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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

"""Updates a Cloud NetApp Host Group."""

from googlecloudsdk.api_lib.netapp.host_groups import client as host_groups_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.host_groups import flags as host_groups_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.Hidden
class Update(base.UpdateCommand):
  """Update a Cloud NetApp Host Group."""

  detailed_help = {
      'DESCRIPTION': """\
          Update a Cloud NetApp Host Group and its specified parameters.
          """,
      'EXAMPLES': """\
          The following command updates a Host Group named NAME and its specified parameters:

              $ {command} NAME --location=us-central1 --description="new description" --hosts="host3,host4" --update-labels=key2=val2
          """,
  }

  @staticmethod
  def Args(parser):
    host_groups_flags.AddHostGroupUpdateArgs(parser)

  def Run(self, args):
    """Update a Cloud NetApp Host Group in the current project."""
    host_group_ref = args.CONCEPTS.host_group.Parse()

    client = host_groups_client.HostGroupsClient(self.ReleaseTrack())
    labels_diff = labels_util.Diff.FromUpdateArgs(args)
    original_host_group = client.GetHostGroup(host_group_ref)

    # Update labels
    if labels_diff.MayHaveUpdates():
      labels = labels_diff.Apply(
          client.messages.HostGroup.LabelsValue, original_host_group.labels
      ).GetOrNone()
    else:
      labels = None

    host_group = client.ParseUpdatedHostGroupConfig(
        original_host_group,
        hosts=args.hosts,
        description=args.description,
        labels=labels,
    )

    updated_fields = []
    if args.IsSpecified('description'):
      updated_fields.append('description')
    if args.IsSpecified('hosts'):
      updated_fields.append('hosts')
    if (labels is not None) and (
        args.IsSpecified('update_labels')
        or args.IsSpecified('remove_labels')
        or args.IsSpecified('clear_labels')
    ):
      updated_fields.append('labels')

    update_mask = ','.join(updated_fields)
    result = client.UpdateHostGroup(
        host_group_ref, host_group, update_mask, args.async_
    )
    if args.async_:
      command = 'gcloud {} netapp host-groups describe {} --location {}'.format(
          self.ReleaseTrack().prefix,
          host_group_ref.Name(),
          host_group_ref.locationsId,
      )
      log.status.Print(
          'Check the status of the updated host group by describing it:\n  '
          '$ {} '.format(command)
      )
    return result
