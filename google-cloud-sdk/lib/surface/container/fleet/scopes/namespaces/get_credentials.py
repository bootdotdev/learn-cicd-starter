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
"""Fetch Hub-registered cluster credentials for Connect Gateway."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.container.fleet import util as fleet_util
from googlecloudsdk.command_lib.container.fleet import gateway
from googlecloudsdk.command_lib.container.fleet import resources


class GetCredentials(gateway.GetCredentialsCommand):
  """Fetch credentials for a membership with a particular namespace.

  ## EXAMPLES

    Get the Connect Gateway kubeconfig for global membership `MEMBERSHIP`,
    using namespace `NAMESPACE` in the config:

      $ {command} NAMESPACE --membership=MEMBERSHIP --membership-location=global
        --set-namespace-in-config=true

    Get the Connect Gateway kubeconfig for global membership `MEMBERSHIP`:

      $ {command} NAMESPACE --membership=MEMBERSHIP --membership-location=global
  """

  @classmethod
  def Args(cls, parser):
    parser.add_argument(
        'NAMESPACE',
        type=str,
        help='Name of the namespace for which to get access to memberships.')
    parser.add_argument(
        '--membership',
        type=str,
        # TODO(b/240565379): filter for memberships with the namespace
        help=textwrap.dedent("""\
          Membership ID to get credentials from. If not provided, a
          prompt will offer a list of memberships in the fleet."""),
    )
    parser.add_argument(
        '--membership-location',
        type=str,
        help=textwrap.dedent("""\
            The location of the membership resource, e.g. `us-central1`.
            If not specified, defaults to `global`.
          """),
    )
    parser.add_argument(
        '--set-namespace-in-config',
        type=bool,
        help=textwrap.dedent("""\
            If true, the default namespace for the context in the generated
            kubeconfig will be set to the Fleet namespace
            (i.e. the name given as the positional argument in this command).

            Otherwise, no default namespace will be set, functioning the same as
            `gcloud container fleet memberships get-credentials`.
            """),
    )
    # TODO(b/368039642): Remove once we're sure server-side generation is stable
    parser.add_argument(
        '--use-client-side-generation',
        action='store_true',
        required=False,
        hidden=True,
        help=textwrap.dedent("""\
          Generate the kubeconfig locally rather than generating it using an API
          call.
        """),
    )

  def Run(self, args):
    if args.set_namespace_in_config:
      context_namespace = args.NAMESPACE
    else:
      context_namespace = None

    if args.membership:
      membership_id = args.membership
      location = args.membership_location or 'global'
    else:
      membership = resources.PromptForMembership()
      membership_id = fleet_util.MembershipShortname(membership)
      location = fleet_util.MembershipLocation(membership)

    if args.use_client_side_generation:
      self.RunGetCredentials(membership_id, location, context_namespace)
    else:
      self.RunServerSide(
          membership_id,
          location,
          arg_namespace=context_namespace,
      )
