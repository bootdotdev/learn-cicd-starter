# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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

"""Command for listing managed instance group resize requests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import request_helper
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute import scope as compute_scope
from googlecloudsdk.command_lib.compute.instance_groups import flags as instance_groups_flags
from googlecloudsdk.command_lib.compute.instance_groups.managed.resize_requests import flags as rr_flags

DETAILED_HELP = {
    'DESCRIPTION':
        """\
        {command} displays all Compute Engine resize requests in a managed
        instance group.
      """,
    'EXAMPLES':
        """\
        To list all resize requests in a managed instance group in table form,
        run:

        $ {command} example-managed-instance-group --zone=us-central1-a

        To list the URIs of all resize requests in a managed instance group, run:

        $ {command} example-managed-instance-group --zone=us-central1-a --uri
    """
}


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List Compute Engine managed instance group resize requests."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    rr_flags.AddOutputFormat(parser, base.ReleaseTrack.GA)
    instance_groups_flags.MakeZonalInstanceGroupManagerArg().AddArgument(
        parser)

  def Run(self, args):
    """Creates and issues an instanceGroupManagerResizeRequests.list request.

    Args:
      args: the argparse arguments that this command was invoked with.

    Returns:
      List of resize requests.
    """

    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    resource_arg = instance_groups_flags.MakeZonalInstanceGroupManagerArg()
    igm_ref = self._GetIgmRef(args, holder, resource_arg)
    return self._Run(holder.client, igm_ref)

  def _GetIgmRef(self, args, holder, resource_arg):
    return resource_arg.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.ZONE,
        scope_lister=flags.GetDefaultScopeLister(holder.client),
    )

  def _Run(self, client, igm_ref):
    if igm_ref.Collection() == 'compute.instanceGroupManagers':
      service = client.apitools_client.instanceGroupManagerResizeRequests
      request = (
          client.messages.ComputeInstanceGroupManagerResizeRequestsListRequest(
              instanceGroupManager=igm_ref.Name(),
              zone=igm_ref.zone,
              project=igm_ref.project,
          )
      )
    elif igm_ref.Collection() == 'compute.regionInstanceGroupManagers':
      service = client.apitools_client.regionInstanceGroupManagerResizeRequests
      request = client.messages.ComputeRegionInstanceGroupManagerResizeRequestsListRequest(
          instanceGroupManager=igm_ref.Name(),
          region=igm_ref.region,
          project=igm_ref.project,
      )
    else:
      raise ValueError(
          'Unknown reference type {0}'.format(igm_ref.Collection())
      )

    errors = []
    results = list(request_helper.MakeRequests(
        requests=[(service, 'List', request)],
        http=client.apitools_client.http,
        batch_url=client.batch_url,
        errors=errors))

    if errors:
      utils.RaiseToolException(errors)
    return results


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class ListBeta(List):
  """List Compute Engine managed instance group resize requests."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    rr_flags.AddOutputFormat(parser, base.ReleaseTrack.BETA)
    instance_groups_flags.MULTISCOPE_INSTANCE_GROUP_MANAGER_ARG.AddArgument(
        parser)

  def Run(self, args):
    """Creates and issues an instanceGroupManagerResizeRequests.list request."""

    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    resource_arg = instance_groups_flags.MULTISCOPE_INSTANCE_GROUP_MANAGER_ARG
    igm_ref = self._GetIgmRef(args, holder, resource_arg)
    return self._Run(holder.client, igm_ref)

  def _GetIgmRef(self, args, holder, resource_arg):
    igm_ref = resource_arg.ResolveAsResource(
        args,
        holder.resources,
        default_scope=compute_scope.ScopeEnum.ZONE,
        scope_lister=flags.GetDefaultScopeLister(holder.client),
    )
    return igm_ref


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(ListBeta):
  """List Compute Engine managed instance group resize requests."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    rr_flags.AddOutputFormat(parser, base.ReleaseTrack.ALPHA)
    instance_groups_flags.MULTISCOPE_INSTANCE_GROUP_MANAGER_ARG.AddArgument(
        parser)
