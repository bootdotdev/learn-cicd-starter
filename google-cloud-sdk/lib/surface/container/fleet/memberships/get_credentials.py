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
"""Fetch Hub-registered cluster credentials for Connect Gateway."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.container.fleet import util as fleet_util
from googlecloudsdk.command_lib.container.fleet import gateway
from googlecloudsdk.command_lib.container.fleet import resources


class GetCredentials(gateway.GetCredentialsCommand):
  """Fetch credentials for a fleet-registered cluster to be used in Connect Gateway.

  {command} updates the `kubeconfig` file with the appropriate credentials and
  endpoint information to send `kubectl` commands to a fleet-registered and
  -connected cluster through the Connect Gateway service.

  It takes a project, passed through by set defaults or flags. By default,
  credentials are written to `$HOME/.kube/config`. You can provide an alternate
  path by setting the `KUBECONFIG` environment variable. If `KUBECONFIG`
  contains multiple paths, the first one is used.

  Upon success, this command will switch the current context to the target
  cluster if other contexts are already present in the `kubeconfig` file.

  ## EXAMPLES

    Get the Gateway kubeconfig for a globally registered cluster:

      $ {command} my-cluster
      $ {command} my-cluster --location=global

    Get the Gateway kubeconfig for a cluster registered in us-central1:

      $ {command} my-cluster --location=us-central1
  """

  @classmethod
  def Args(cls, parser):
    resources.AddMembershipResourceArg(
        parser,
        membership_help=textwrap.dedent("""\
          The membership name that you choose to uniquely represent the cluster
          being registered in the fleet.
        """),
        location_help=textwrap.dedent("""\
          The location of the membership resource, e.g. `us-central1`.
          If not specified, attempts to automatically choose the correct region.
        """),
        membership_required=True,
        positional=True,
    )

    # TODO(b/368039642): Remove once we're sure server-side generation is stable
    parser.add_argument(
        '--use-client-side-generation',
        action='store_true',
        required=False,
        hidden=True,
        help=textwrap.dedent("""\
          Generate the kubeconfig locally rather than generating
          it using an API call.
        """),
    )

    parser.add_argument(
        '--force-use-agent',
        action='store_true',
        required=False,
        hidden=True,
        help=textwrap.dedent("""\
          Force the use of Connect Agent-based transport.
        """),
    )

  def Run(self, args):
    membership_name = resources.ParseMembershipArg(args)
    location = fleet_util.MembershipLocation(membership_name)
    membership_id = fleet_util.MembershipShortname(membership_name)

    if args.use_client_side_generation:
      self.RunGetCredentials(membership_id, location)
    else:
      self.RunServerSide(
          membership_id, location, force_use_agent=args.force_use_agent
      )
