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

"""Create a Cloud NetApp Host Group."""

from googlecloudsdk.api_lib.netapp.host_groups import client as host_groups_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.netapp.host_groups import flags as host_groups_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class Create(base.CreateCommand):
  """Create a Cloud NetApp Host Group."""

  _RELEASE_TRACK = base.ReleaseTrack.ALPHA

  detailed_help = {
      'DESCRIPTION': """\
          Create a Cloud NetApp Host Group.
          """,
      'EXAMPLES': """\
          The following command creates a Host Group named NAME using the required arguments:

              $ {command} NAME --location=us-central1 --type=ISCSI_INITIATOR --hosts=host1,host2 --os-type=LINUX
          """,
  }

  @staticmethod
  def Args(parser):
    host_groups_flags.AddHostGroupCreateArgs(parser)

  def Run(self, args):
    """Create a Cloud NetApp Host Group in the current project."""
    host_group_ref = args.CONCEPTS.host_group.Parse()

    client = host_groups_client.HostGroupsClient(self._RELEASE_TRACK)

    host_group_type = host_groups_flags.GetHostGroupTypeEnumFromArg(
        args.type, client.messages
    )
    os_type = host_groups_flags.GetHostGroupOsTypeEnumFromArg(
        args.os_type, client.messages
    )
    labels = labels_util.ParseCreateArgs(
        args, client.messages.HostGroup.LabelsValue
    )

    host_group = client.ParseHostGroupConfig(
        name=host_group_ref.RelativeName(),
        host_group_type=host_group_type,
        hosts=args.hosts,
        os_type=os_type,
        description=args.description,
        labels=labels,
    )

    result = client.CreateHostGroup(host_group_ref, args.async_, host_group)
    if args.async_:
      command = 'gcloud {} netapp host-groups list'.format(
          self.ReleaseTrack().prefix
      )
      log.status.Print(
          'Check the status of the new host group by listing all host groups:\n'
          '$ {} '.format(command)
      )
    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.Hidden
class CreateBeta(Create):
  """Create a Cloud NetApp Host Group."""

  _RELEASE_TRACK = base.ReleaseTrack.BETA
