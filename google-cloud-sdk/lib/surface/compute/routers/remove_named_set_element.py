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

"""Command for adding an element to an existing named set of a Compute Engine router."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.routers import flags
from googlecloudsdk.command_lib.compute.routers import route_policy_utils


@base.Hidden
@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class RemoveNamedSetElement(base.UpdateCommand):
  """Remove an element from a named set of a Compute Engine router."""

  ROUTER_ARG = None

  @classmethod
  def Args(cls, parser):
    RemoveNamedSetElement.ROUTER_ARG = flags.RouterArgument()
    RemoveNamedSetElement.ROUTER_ARG.AddArgument(
        parser, operation_type='update'
    )
    parser.add_argument(
        '--set-name',
        help="""Name of the match set.""",
        required=True,
    )
    parser.add_argument(
        '--set-element',
        help="""CEL expression for the element.""",
        required=True,
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages
    service = holder.client.apitools_client.routers

    router_ref = RemoveNamedSetElement.ROUTER_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    named_set = service.GetNamedSet(
        messages.ComputeRoutersGetNamedSetRequest(
            **router_ref.AsDict(), namedSet=args.set_name
        )
    ).resource
    element = route_policy_utils.FindNamedSetElementOrRise(
        resource=named_set, element_cel=args.set_element
    )
    named_set.elements.remove(element)
    # Cleared list fields need to be explicitly identified for Patch API.
    cleared_fields = [] if named_set.elements else ['elements']

    request = (
        service,
        'PatchNamedSet',
        messages.ComputeRoutersPatchNamedSetRequest(
            **router_ref.AsDict(),
            namedSet=named_set,
        ),
    )
    with client.apitools_client.IncludeFields(cleared_fields):
      result = client.MakeRequests([request])
    return result
