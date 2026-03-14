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
"""Command to add project-level and fleet scope-level IAM bindings and create a fleet scope RBAC role binding for an app operator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import random

from apitools.base.py import encoding
from googlecloudsdk.api_lib.cloudresourcemanager import projects_api
from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util as api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.scopes import util as scopes_util
from googlecloudsdk.command_lib.iam import iam_util
from googlecloudsdk.command_lib.projects import util as projects_util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class AddAppOperatorBinding(base.CreateCommand):
  """Add project-level and fleet scope-level IAM bindings and create a fleet scope RBAC role binding for an app operator principal.

  One binding consists of an app operator principal (user/group) and a role
  (view/edit/admin or a custom role).

  This command sets up the different permissions required for an app operator,
  including usage of fleet scopes, connect gateway, logging, and metrics. The
  authoritative list for adding the permissions is the existing RBAC role
  bindings under the specified scope.

  This command can fail for the following reasons:
  * The scope specified does not exist.
  * The user does not have access to the specified scope.
  * The principal specified already has another binding for the scope.

  ## EXAMPLES

  The following command:

    $ {command} SCOPE --role=view --group=people@google.com --project=PROJECT_ID

  * adds IAM policy binding: roles/gkehub.scopeViewer on `SCOPE`
  * adds IAM policy binding: roles/gkehub.scopeViewerProjectLevel on
  `PROJECT_ID`
  * adds IAM policy binding: roles/logging.viewAccessor on `PROJECT_ID` with
  condition where bucket corresponds to `SCOPE`
  * creates fleet scope RBAC role binding: role `view` with a random ID
  for group `people@google.com`.

  ---

  The following command:

    $ {command} SCOPE --role=edit --user=person@google.com --project=PROJECT_ID

  * adds IAM policy binding: roles/gkehub.scopeEditor on `SCOPE`
  * adds IAM policy binding: roles/gkehub.scopeEditorProjectLevel on
  `PROJECT_ID`
  * adds IAM policy binding: roles/logging.viewAccessor on `PROJECT_ID` with
  condition where bucket corresponds to `SCOPE`
  * creates fleet scope RBAC role binding: role `edit` with a random ID
  for user `person@google.com`.

  ---

  The following command:

    $ {command} SCOPE --role=admin --user=person@google.com --project=PROJECT_ID

  * adds IAM policy binding: roles/gkehub.scopeAdmin on `SCOPE`
  * adds IAM policy binding: roles/gkehub.scopeEditorProjectLevel on
  `PROJECT_ID`
  * adds IAM policy binding: roles/logging.viewAccessor on `PROJECT_ID` with
  condition where bucket corresponds to `SCOPE`
  * creates fleet scope RBAC role binding: role `admin` with a random ID
  for user `person@google.com`.

  ---

  The following command:

    $ {command} SCOPE --custom-role=my-custom-role --user=person@google.com
    --project=PROJECT_ID

  * adds IAM policy binding: roles/gkehub.scopeViewer on `SCOPE`
  * adds IAM policy binding: roles/gkehub.scopeEditorProjectLevel on
  `PROJECT_ID`
  * adds IAM policy binding: roles/logging.viewAccessor on `PROJECT_ID` with
  condition where bucket corresponds to `SCOPE`
  * creates fleet scope RBAC role binding: role `my-custom-role` with a random
  ID for user `person@google.com`.

  For any tailored IAM permissions required when using a custom role, the user
  or group can separately be granted additional IAM permissions on the project.
  """

  @classmethod
  def Args(cls, parser):
    resources.AddScopeResourceArg(
        parser,
        'SCOPE',
        api_util.VERSION_MAP[cls.ReleaseTrack()],
        scope_help=(
            'Name of the fleet scope for adding IAM and RBAC role bindings.'
        ),
        required=True,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--user',
        type=str,
        help='User for the role binding.',
    )
    group.add_argument(
        '--group',
        type=str,
        help='Group for the role binding.',
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
    project = args.project
    if project is None:
      project = properties.VALUES.core.project.Get()
    fleetclient = client.FleetClient(release_track=self.ReleaseTrack())
    scope_arg = args.CONCEPTS.scope.Parse()
    scope_id = scope_arg.Name()
    scope_path = scope_arg.RelativeName()
    iam_member = scopes_util.IamMemberFromRbac(args.user, args.group)
    # If a custom role is specified, the scope-level role is view and the
    # project-level role is edit.
    if args.custom_role is not None:
      iam_scope_level_role = scopes_util.IamScopeLevelScopeRoleFromRbac(
          args.custom_role
      )
      iam_project_level_role = scopes_util.IamProjectLevelScopeRoleFromRbac(
          args.custom_role
      )
    else:
      iam_scope_level_role = scopes_util.IamScopeLevelScopeRoleFromRbac(
          args.role
      )
      iam_project_level_role = scopes_util.IamProjectLevelScopeRoleFromRbac(
          args.role
      )
    custom_role = args.custom_role
    scope_rrbs = fleetclient.ListScopeRBACRoleBindings(project, scope_id)
    for existing_rrb in scope_rrbs:
      if existing_rrb.user == args.user and existing_rrb.group == args.group:
        if existing_rrb.role.predefinedRole:
          printed_role = encoding.MessageToPyValue(existing_rrb.role)[
              'predefinedRole'
          ].lower()
        else:
          printed_role = existing_rrb.role.customRole
        log.error(
            '`{}` already has role `{}` for scope `{}` via an existing RBAC'
            ' role binding: `{}`'.format(
                iam_member,
                printed_role,
                scope_id,
                existing_rrb.name,
            )
        )
        # It's enough to just show the first matching scope rrb.
        return

    # Prompt the user to confirm the bindings to be added.
    if custom_role:
      printed_role = custom_role
    else:
      printed_role = args.role
    if console_io.CanPrompt():
      console_io.PromptContinue(
          message=(
              'The command:\n  * adds IAM policy binding: `{scope_role}` on'
              ' scope `{scope}`\n  * adds IAM policy binding: `{proj_role}` on'
              ' project `{proj}`\n  * adds IAM policy binding:'
              ' `roles/logging.viewAccessor` on project `{proj}` with a'
              ' condition where the bucket corresponds to scope `{scope}`\n  *'
              ' creates a fleet scope RBAC role binding: role `{arg_role}` for'
              ' `{member}`'.format(
                  scope=scope_id,
                  proj=project,
                  arg_role=printed_role,
                  member=iam_member,
                  scope_role=iam_scope_level_role,
                  proj_role=iam_project_level_role,
              )
          ),
          prompt_string='Do you want to continue',
          cancel_on_no=True,
      )

    project_ref = projects_util.ParseProject(project)
    projects_api.AddIamPolicyBinding(
        project_ref,
        iam_member,
        iam_project_level_role,
    )
    condition = scopes_util.ScopeLogViewCondition(project, scope_id)
    iam_util.ValidateConditionArgument(
        condition, iam_util.CONDITION_FORMAT_EXCEPTION
    )
    projects_api.AddIamPolicyBindingWithCondition(
        project_ref,
        iam_member,
        'roles/logging.viewAccessor',
        condition,
    )
    log.Print('Added project-level IAM bindings')

    scope_iam_policy = fleetclient.GetScopeIamPolicy(scope_path)
    iam_util.AddBindingToIamPolicy(
        api_util.GetMessagesModule(self.ReleaseTrack()).Binding,
        scope_iam_policy,
        iam_member,
        iam_scope_level_role,
    )
    fleetclient.SetScopeIamPolicy(scope_path, scope_iam_policy)
    log.Print('Added scope-level IAM binding')

    # Use a 16-character hex-like random ID for the scope RBAC RoleBinding.
    scope_rrb = (
        scope_path
        + '/rbacrolebindings/'
        + ''.join([random.choice('abcdef0123456789') for _ in range(16)])
    )
    labels_diff = labels_util.Diff(additions=args.labels)
    labels = labels_diff.Apply(
        fleetclient.messages.RBACRoleBinding.LabelsValue, None
    ).GetOrNone()
    return fleetclient.CreateScopeRBACRoleBinding(
        name=scope_rrb,
        role=args.role,
        custom_role=custom_role,
        user=args.user,
        group=args.group,
        labels=labels,
    )
