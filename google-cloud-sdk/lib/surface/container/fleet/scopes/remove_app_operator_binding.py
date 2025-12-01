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
"""Command to remove project-level and fleet scope-level IAM bindings and delete a fleet scope RBAC role binding for an app operator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re

from apitools.base.py import encoding
from googlecloudsdk.api_lib.cloudresourcemanager import projects_api
from googlecloudsdk.api_lib.container.fleet import client
from googlecloudsdk.api_lib.container.fleet import util as api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet import util
from googlecloudsdk.command_lib.container.fleet.scopes import util as scopes_util
from googlecloudsdk.command_lib.iam import iam_util
from googlecloudsdk.command_lib.projects import util as projects_util
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class RemoveAppOperatorBinding(base.DeleteCommand):
  """Remove project-level and fleet scope-level IAM bindings and delete a fleet scope RBAC role binding for an app operator principal.

  One binding consists of an app operator principal (user/group) and a role
  (view/edit/admin).

  This command unsets the different permissions required for an app operator,
  including usage of fleet scopes, connect gateway, logging, and metrics. The
  authoritative list for removing the permissions is the existing RBAC role
  bindings under the specified scope.

  This command can fail for the following reasons:
  * The scope specified does not exist.
  * The user does not have access to the specified scope.
  * The principal specified does not any binding for the scope.
  * The principal specified has bindings with different roles for the scope.

  ## EXAMPLES

  The following command:

    $ {command} SCOPE --group=people@google.com --project=PROJECT_ID

  assuming the group already has the `view` role:
  * removes IAM policy binding: roles/gkehub.scopeViewer from `SCOPE`
  * removes IAM policy binding: roles/gkehub.scopeViewerProjectLevel from
  `PROJECT_ID` if the group does not have the `view` role for any other scope
  under the project
  * removes IAM policy binding: roles/logging.viewAccessor from `PROJECT_ID`
  condition where bucket corresponds to `SCOPE`
  * deletes existing fleet scope RBAC role binding: role `view` for group
  `people@google.com`.

  ---

  The following command:

    $ {command} SCOPE --user=person@google.com --project=PROJECT_ID

  assuming the user already has the `edit` role:
  * removes IAM policy binding: roles/gkehub.scopeEditor from `SCOPE`
  * removes IAM policy binding: roles/gkehub.scopeEditorProjectLevel from
  `PROJECT_ID` if the user does not have the `edit`/`admin` role for any other
  scope under the project
  * removes IAM policy binding: roles/logging.viewAccessor from `PROJECT_ID`
  condition where bucket corresponds to `SCOPE`
  * deletes existing fleet scope RBAC role binding: role `edit` for user
  `person@google.com`.

  ---

  The following command:

    $ {command} SCOPE --user=person@google.com --project=PROJECT_ID

  assuming the user already has a custom role:
  * removes IAM policy binding: roles/gkehub.scopeViewer from `SCOPE`
  * removes IAM policy binding: roles/gkehub.scopeEditorProjectLevel from
  `PROJECT_ID`  if the user does not have the `edit`/`admin` role for any other
  scope under the project
  * removes IAM policy binding: roles/logging.viewAccessor from `PROJECT_ID`
  condition where bucket corresponds to `SCOPE`
  * deletes existing fleet scope RBAC role binding: role `admin` for user
  `person@google.com`.

  ---

  The following command:

    $ {command} SCOPE --user=person@google.com --project=PROJECT_ID

  assuming the user already has the `admin` role:
  * removes IAM policy binding: roles/gkehub.scopeAdmin from `SCOPE`
  * removes IAM policy binding: roles/gkehub.scopeEditorProjectLevel from
  `PROJECT_ID`  if the user does not have the `edit`/`admin` role for any other
  scope under the project
  * removes IAM policy binding: roles/logging.viewAccessor from `PROJECT_ID`
  condition where bucket corresponds to `SCOPE`
  * deletes existing fleet scope RBAC role binding: role `admin` for user
  `person@google.com`.
  """

  @classmethod
  def Args(cls, parser):
    resources.AddScopeResourceArg(
        parser,
        'SCOPE',
        api_util.VERSION_MAP[cls.ReleaseTrack()],
        scope_help=(
            'Name of the fleet scope for removing IAM and RBAC role bindings.'
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

  def Run(self, args):
    project = args.project
    if project is None:
      project = properties.VALUES.core.project.Get()
    project_ref = projects_util.ParseProject(project)
    fleetclient = client.FleetClient(release_track=self.ReleaseTrack())
    scope_arg = args.CONCEPTS.scope.Parse()
    scope_id = scope_arg.Name()
    scope_path = scope_arg.RelativeName()
    iam_member = scopes_util.IamMemberFromRbac(args.user, args.group)

    matching_scope_rrbs = []
    role = ''
    scope_rrbs = fleetclient.ListScopeRBACRoleBindings(project, scope_id)
    for scope_rrb in scope_rrbs:
      if scope_rrb.user == args.user and scope_rrb.group == args.group:
        if not role:
          role = scopes_util.ScopeRbacRoleString(scope_rrb.role)
        elif role != scopes_util.ScopeRbacRoleString(scope_rrb.role):
          log.error(
              '`{}` has more than one role (`{}` and `{}`) for scope `{}` via'
              ' existing RBAC role bindings. Please remove unexpected bindings'
              ' invdividually and retry.'.format(
                  iam_member,
                  role,
                  scopes_util.ScopeRbacRoleString(scope_rrb.role),
                  scope_id,
              )
          )
          return
        matching_scope_rrbs.append(scope_rrb)
    if not matching_scope_rrbs:
      log.error(
          '`{}` does not have any role for scope `{}` via existing RBAC role'
          ' bindings.'.format(iam_member, scope_id)
      )
      return

    iam_scope_level_role = scopes_util.IamScopeLevelScopeRoleFromRbac(role)
    iam_project_level_role = scopes_util.IamProjectLevelScopeRoleFromRbac(role)

    # We don't want to remove the binding for the project-level scope role if
    # app operator still needs the same access for other scopes.
    another_scope_needs_project_level_permission = False
    scopes = fleetclient.ListScopes(project)
    for scope in scopes:
      if scope.name == scope_path:
        continue
      scope_rrbs = fleetclient.ListScopeRBACRoleBindings(
          project, util.ResourceIdFromPath(scope.name)
      )
      roles_to_check = {
          'view': ['view'],
          # `edit` and `admin` roles need the same project-level role,
          # i.e., `roles/gkehub.scopeEditorProjectLevel`.
          'edit': ['edit', 'admin'],
          'admin': ['edit', 'admin'],
      }
      for scope_rrb in scope_rrbs:
        # Custom roles have `roles/gkehub.scopeEditorProjectLevel` permissions.
        for r in roles_to_check.get(role, ['edit', 'admin']):
          if bindings_match(scope_rrb, r, args.user, args.group):
            another_scope_needs_project_level_permission = True

    if console_io.CanPrompt():
      prompt_msg = (
          'The command:\n  * removes IAM policy binding: `{}` from scope `{}`'
          .format(iam_scope_level_role, scope_id)
      )
      if another_scope_needs_project_level_permission:
        prompt_msg += (
            '\n  * does *not* remove IAM policy binding: `{}` from project `{}`'
            ' as `{}` needs the binding for other scope(s) in the project'
            .format(iam_project_level_role, project, iam_member)
        )
      else:
        prompt_msg += (
            '\n  * removes IAM policy binding: `{}` from project `{}`'.format(
                iam_project_level_role, project
            )
        )
      prompt_msg += (
          '\n  * removes IAM policy binding: `roles/logging.viewAccessor` from'
          ' project `{}` with a condition where the bucket corresponds to scope'
          ' `{}`\n  * deletes existing fleet scope RBAC role binding: role `{}`'
          ' for `{}`'.format(project, scope_id, role, iam_member)
      )

      console_io.PromptContinue(
          message=prompt_msg,
          prompt_string='Do you want to continue',
          cancel_on_no=True,
      )

    if not another_scope_needs_project_level_permission:
      projects_api.RemoveIamPolicyBinding(
          project_ref,
          iam_member,
          iam_project_level_role,
      )
      log.Print(
          'Removed project-level binding for `{}`'.format(
              iam_project_level_role
          )
      )

    condition = scopes_util.ScopeLogViewCondition(project, scope_id)
    iam_util.ValidateConditionArgument(
        condition, iam_util.CONDITION_FORMAT_EXCEPTION
    )
    projects_api.RemoveIamPolicyBindingWithCondition(
        project_ref,
        iam_member,
        'roles/logging.viewAccessor',
        condition,
        False,  # Only consider the given condition.
    )
    log.Print(
        'Removed conditional project-level binding for'
        ' `roles/logging.viewAccessor`'
    )

    scope_iam_policy = fleetclient.GetScopeIamPolicy(scope_path)
    iam_util.RemoveBindingFromIamPolicy(
        scope_iam_policy,
        iam_member,
        iam_scope_level_role,
    )
    fleetclient.SetScopeIamPolicy(scope_path, scope_iam_policy)
    log.Print('Removed scope-level IAM binding')

    if len(matching_scope_rrbs) > 1:
      log.warning(
          'More than one RBAC role binding found for `{}` with role `{}` under'
          ' scope `{}`; deleting all of them...'.format(
              iam_member, role, scope_id
          )
      )
    for scope_rrb in matching_scope_rrbs:
      fleetclient.DeleteScopeRBACRoleBinding(scope_rrb.name)


def bindings_match(scope_rrb, role, user, group):
  return (
      re.search(
          role,
          encoding.MessageToPyValue(scope_rrb.role)['predefinedRole'],
          re.IGNORECASE,
      )
      and scope_rrb.user == user
      and scope_rrb.group == group
  )
