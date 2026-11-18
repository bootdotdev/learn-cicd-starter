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
"""Delete instant snapshot group command."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.instant_snapshot_groups import flags as isg_flags


DETAILED_HELP = {  # Dict[str, str]
    'brief': 'Delete an instant snapshot group.',
}


def _CommonArgs(parser):
  """A helper function to build args based on different API version."""
  Delete.ISG_ARG = isg_flags.MakeInstantSnapshotGroupArg(plural=True)
  Delete.ISG_ARG.AddArgument(parser, operation_type='delete')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete a Compute Engine instant snapshot group."""

  def _GetCommonScopeNameForRefs(self, refs):
    """Gets common scope for references."""
    has_zone = any(hasattr(ref, 'zone') for ref in refs)
    has_region = any(hasattr(ref, 'region') for ref in refs)

    if has_zone and not has_region:
      return 'zone'
    elif has_region and not has_zone:
      return 'region'
    else:
      return None

  def _CreateDeleteRequests(self, client, isg_refs):
    """Returns a list of delete messages for instant snapshot groups."""

    messages = client.MESSAGES_MODULE
    requests = []
    for isg_ref in isg_refs:
      if isg_ref.Collection() == 'compute.instantSnapshotGroups':
        service = client.instantSnapshotGroups
        request = messages.ComputeInstantSnapshotGroupsDeleteRequest(
            instantSnapshotGroup=isg_ref.Name(),
            project=isg_ref.project,
            zone=isg_ref.zone)
      elif isg_ref.Collection() == 'compute.regionInstantSnapshotGroups':
        service = client.regionInstantSnapshotGroups
        request = messages.ComputeRegionInstantSnapshotGroupsDeleteRequest(
            instantSnapshotGroup=isg_ref.Name(),
            project=isg_ref.project,
            region=isg_ref.region)
      else:
        raise ValueError('Unknown reference type {0}'.format(
            isg_ref.Collection()))

      requests.append((service, 'Delete', request))
    return requests

  @classmethod
  def Args(cls, parser):
    _CommonArgs(parser)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack())

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    isg_ref = Delete.ISG_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )

    scope_name = self._GetCommonScopeNameForRefs(isg_ref)

    utils.PromptForDeletion(isg_ref, scope_name=scope_name, prompt_title=None)

    requests = list(
        self._CreateDeleteRequests(client.apitools_client, isg_ref))

    return client.MakeRequests(requests)

  def Run(self, args):
    return self._Run(args)
