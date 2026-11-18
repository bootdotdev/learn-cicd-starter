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
"""Command to create a fleet scope RBAC RoleBinding."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.util.args import labels_util


@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an RBAC RoleBinding.

  This command can fail for the following reasons:
  * The RBAC RoleBinding already exists.
  * The caller does not have permission to access the given scope.

  ## EXAMPLES

  To create an admin RBAC RoleBinding `RBRB` in scope `SCOPE` for user
  `person@google.com`, run:

    $ {command} RBRB --scope=SCOPE --role=admin
    --user=person@google.com

  To create a viewer RBAC RoleBinding `RBRB` in scope `SCOPE` for group
  `people@google.com`, run:

    $ {command} RBRB --scope=SCOPE --role=viewer
    --group=people@google.com

  To create an RBAC RoleBinding with a custom role `custom-role` in scope
  `SCOPE` for user `person@google.com`, run:

    $ {command} RBRB --scope=SCOPE --role=admin
    --user=person@google.com
    --custom-role=custom-role
  """

  @classmethod
  def Args(cls, parser):
    resources.AddScopeRBACResourceArg(
        parser,
        api_version=util.VERSION_MAP[cls.ReleaseTrack()],
        rbacrb_help=(
            'Name of the RBAC RoleBinding to be created. '
            'Must comply with RFC 1123 (up to 63 characters, '
            "alphanumeric and '-')"
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--user',
        type=str,
        help='User for the RoleBinding.',
    )
    group.add_argument(
        '--group',
        type=str,
        help='Group for the RoleBinding.',
    )
    roledef = parser.add_mutually_exclusive_group(required=True)
    roledef.add_argument(
        '--role',
        choices=['admin', 'edit', 'view'],
        help='Predefined role to assign to principal (admin, edit, view).',
    )
    roledef.add_argument(
        '--custom-role',
        type=str,
        help='Custom role to assign to principal.',
    )
    labels_util.AddCreateLabelsFlags(parser)

  def Run(self, args):
    fleetclient = client.FleetClient(release_track=self.ReleaseTrack())
    labels_diff = labels_util.Diff(additions=args.labels)
    labels = labels_diff.Apply(
        fleetclient.messages.RBACRoleBinding.LabelsValue, None
    ).GetOrNone()
    # Only set the custom role field if the release track is alpha.
    custom_role = args.custom_role
    return fleetclient.CreateScopeRBACRoleBinding(
        resources.RBACResourceName(args),
        role=args.role,
        custom_role=custom_role,
        user=args.user,
        group=args.group,
        labels=labels,
    )
