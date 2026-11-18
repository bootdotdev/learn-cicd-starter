# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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

"""Command for describing subnetworks."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.networks.subnets import flags
from googlecloudsdk.command_lib.util.apis import arg_utils


def _DetailedHelp():
  return {
      'brief': 'Describe a Compute Engine subnetwork.',
      'DESCRIPTION': """\
          *{command}* displays all data associated with a Compute Engine
          subnetwork.
      """,
      'EXAMPLES': """\
        To display all data associated with subnetwork subnet-1, run:

        $ {command} subnet-1
      """,
  }


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Describe(base.DescribeCommand):
  """Describe a Compute Engine subnetwork.

  *{command}* displays all data associated with a Compute Engine
  subnetwork.
  """

  _include_view = True

  SUBNETWORK_ARG = None
  detailed_help = _DetailedHelp()

  @classmethod
  def Args(cls, parser):
    Describe.SUBNETWORK_ARG = flags.SubnetworkArgument()
    Describe.SUBNETWORK_ARG.AddArgument(parser, operation_type='describe')
    if cls._include_view:
      parser.add_argument(
          '--view',
          choices={
              'WITH_UTILIZATION': (
                  'Output includes the IP address utilization data of all'
                  ' subnetwork ranges, showing total allocated and free IPv4'
                  ' and IPv6 IP addresses.'
              ),
          },
          type=arg_utils.ChoiceToEnumName,
          action='append',
          help=(
              'Specifies the information to include in the output.'
          ),
      )

  def _GetSubnetworkViews(self, view, request_message):
    views = []
    for v in view:
      if v == 'WITH_UTILIZATION':
        views.append(request_message.ViewsValueValuesEnum.WITH_UTILIZATION)
    return views

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    subnetwork_ref = Describe.SUBNETWORK_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )

    request = client.messages.ComputeSubnetworksGetRequest(
        **subnetwork_ref.AsDict()
    )

    if self._include_view and args.view:
      request.views = self._GetSubnetworkViews(
          args.view, client.messages.ComputeSubnetworksGetRequest
      )

    return client.MakeRequests(
        [(client.apitools_client.subnetworks, 'Get', request)]
    )[0]


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class DescribeBeta(Describe):
  """Create a subnet in the Beta release track."""

  _include_view = True


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class DescribeAlpha(DescribeBeta):
  """Describe a subnet in the Alpha release track."""

  _include_view = True
