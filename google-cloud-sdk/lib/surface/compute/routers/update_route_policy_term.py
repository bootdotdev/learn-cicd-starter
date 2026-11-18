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
"""Command for updating a route policy term of a Compute Engine router."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.routers import flags
from googlecloudsdk.command_lib.compute.routers import route_policy_utils


@base.UniverseCompatible
class UpdateRoutePolicyTerm(base.UpdateCommand):
  """Updates a term of an existing route policy of a Comute Engine router."""

  ROUTER_ARG = None

  @classmethod
  def Args(cls, parser):
    UpdateRoutePolicyTerm.ROUTER_ARG = flags.RouterArgument()
    UpdateRoutePolicyTerm.ROUTER_ARG.AddArgument(
        parser, operation_type='update'
    )
    parser.add_argument(
        '--policy-name',
        help="""Name of the route policy to which the term should be updated.""",
        required=True,
    )
    parser.add_argument(
        '--priority',
        help="""Order of the term within the policy.""",
        required=True,
        type=arg_parsers.BoundedInt(lower_bound=0, upper_bound=2147483647),
    )
    parser.add_argument(
        '--match',
        help="""CEL expression for matching a route.""",
        required=True,
    )
    parser.add_argument(
        '--actions',
        help="""Semicolon separated CEL expressions for the actions to take when the rule matches.""",
        required=True,
        type=arg_parsers.ArgList(custom_delim_char=';'),
        metavar='ACTION',
    )

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = holder.client.messages

    service = holder.client.apitools_client.routers

    router_ref = UpdateRoutePolicyTerm.ROUTER_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(client),
    )
    route_policy = service.GetRoutePolicy(
        messages.ComputeRoutersGetRoutePolicyRequest(
            **router_ref.AsDict(), policy=args.policy_name
        )
    ).resource

    term = route_policy_utils.FindPolicyTermOrRaise(route_policy, args.priority)
    _UpdatePolicyTermMessage(term, messages, args)
    request = (
        service,
        'PatchRoutePolicy',
        messages.ComputeRoutersPatchRoutePolicyRequest(
            **router_ref.AsDict(),
            routePolicy=route_policy,
        ),
    )
    return client.MakeRequests([request])[0]


def _UpdatePolicyTermMessage(term, messages, args):
  term.match = messages.Expr(expression=args.match)
  term.actions = [
      messages.Expr(expression=cel_expression)
      for cel_expression in args.actions
  ]


UpdateRoutePolicyTerm.detailed_help = {
    'DESCRIPTION': """\
        *{command}* updates a term of a route policy.
        """,
    # pylint: disable=line-too-long
    'EXAMPLES': """\
        To update a term with priority 128 with match `destination == '192.168.0.0/24'` and actions `med.set(12345);asPath.prependSequence([1, 2])` of a route policy `example-policy-name` of a router `example-router` in region `router-region`, run:

          $ {command} example-router --region=router-region --policy-name=example-policy-name --priority=128 --match="destination == '192.168.0.0/24'" --actions="med.set(12345);asPath.prependSequence([1, 2])"

        """,
    # pylint: enable=line-too-long
}
