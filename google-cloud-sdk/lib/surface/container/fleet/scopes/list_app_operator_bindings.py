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
"""Command to list app operator principals corresponding to a fleet scope and their roles based on project-level IAM bindings, fleet scope-level IAM bindings, and fleet scope RBAC role bindings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
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


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class ListAppOperatorBindings(base.ListCommand):
  """List app operator principals corresponding to a fleet scope and their roles based on project-level IAM bindings, fleet scope-level IAM bindings, and fleet scope RBAC role bindings.

  This command lists bindings corresponding to a fleet scope. The bindings,
  which consist of an app operator principal and a role, grant permissions
  required for an app operator, including usage of fleet scopes, connect
  gateway, logging, and metrics. The overarching principal role
  (view/edit/admin, or custom) is determined by (1) the fleet scope RBAC role
  (view, edit, admin or a custom role), (2) the fleet scope-level IAM role
  (roles/gkehub.scopeViewer, roles/gkehub.scopeEditor, or
  roles/gkehub.scopeAdmin), (3) the project-level IAM role
  (roles/gkehub.scopeViewerProjectLevel, or
  roles/gkehub.scopeEditorProjectLevel), and (4) the conditional log view access
  role for the scope bucket.

  This command can fail for the following reasons:
  * The scope specified does not exist.
  * The user does not have access to the specified scope.

  ## EXAMPLES

  The following command lists app operator principals corresponding to `SCOPE`
  under `PROJECT_ID`, their roles, and role details (fleet scope RBAC role,
  fleet scope-level IAM role, project-level IAM role, and log view access):

    $ {command} --scope=SCOPE --project=PROJECT_ID
  """

  @classmethod
  def Args(cls, parser):
    # Table formatting
    parser.display_info.AddFormat(util.APP_OPERATOR_LIST_FORMAT)
    resources.AddScopeResourceArg(
        parser,
        'SCOPE',
        api_util.VERSION_MAP[cls.ReleaseTrack()],
        scope_help=(
            'Name of the fleet scope for listing IAM and RBAC role bindings.'
        ),
        required=True,
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
    has_scope_rrb_permission = True
    has_scope_iam_permission = True
    has_project_iam_permission = True

    principal_to_roles = {}

    try:
      scope_rrbs = fleetclient.ListScopeRBACRoleBindings(project, scope_id)
      derive_scope_rrb_role(scope_rrbs, principal_to_roles)
    except apitools_exceptions.HttpForbiddenError:
      has_scope_rrb_permission = False
      log.warning(
          'You do not have permission to check fleet scope RBAC role bindings.'
          ' This results in incomplete role binding details in the list of app'
          ' operators.'
      )

    try:
      scope_iam_policy = fleetclient.GetScopeIamPolicy(scope_path)
      derive_scope_level_iam_role(scope_iam_policy, principal_to_roles)
    except apitools_exceptions.HttpForbiddenError:
      has_scope_iam_permission = False
      log.warning(
          'You do not have permission to check fleet scope IAM role bindings.'
          ' This results in incomplete role binding details in the list of app'
          ' operators.'
      )

    try:
      project_iam_policy = projects_api.GetIamPolicy(project_ref)
      condition = scopes_util.ScopeLogViewCondition(project, scope_id)
      iam_util.ValidateConditionArgument(
          condition, iam_util.CONDITION_FORMAT_EXCEPTION
      )
      derive_log_view_access_role(
          project_iam_policy, condition, principal_to_roles
      )
      find_project_level_iam_role(project_iam_policy, principal_to_roles)
    except apitools_exceptions.HttpForbiddenError:
      has_project_iam_permission = False
      log.warning(
          'You do not have permission to check project IAM role bindings. This'
          ' results in incomplete role binding details in the list of app'
          ' operators.'
      )

    finalize_roles(
        principal_to_roles,
        has_scope_rrb_permission,
        has_scope_iam_permission,
        has_project_iam_permission,
    )

    bindings = []
    for iam_member in principal_to_roles:
      bindings.append(principal_to_roles[iam_member])
    return bindings


def derive_scope_rrb_role(scope_rrbs, principal_to_roles):
  """Derive the scope RBAC role for the principals in the given list of scope RBAC role bindings."""
  for scope_rrb in scope_rrbs:
    iam_member = scopes_util.IamMemberFromRbac(scope_rrb.user, scope_rrb.group)
    if iam_member not in principal_to_roles:
      init_principal(principal_to_roles, iam_member)

    scope_rrb_role = scopes_util.ScopeRbacRoleString(scope_rrb.role)
    principal_to_roles[iam_member].scope_rrb_role = set_role(
        principal_to_roles[iam_member].scope_rrb_role, scope_rrb_role
    )
    if ',' not in principal_to_roles[iam_member].scope_rrb_role:
      # The overall role can be set to a standard role for now.
      principal_to_roles[iam_member].overall_role = scope_rrb_role


def derive_scope_level_iam_role(scope_iam_policy, principal_to_roles):
  """Derive the scope-level IAM role for the principals in the given scope IAM policy."""
  for binding in scope_iam_policy.bindings:
    for iam_member in binding.members:
      if iam_member not in principal_to_roles:
        init_principal(principal_to_roles, iam_member)

      for scope_iam_role in scopes_util.AllIamScopeLevelScopeRoles():
        if binding.role == scope_iam_role:
          principal_to_roles[iam_member].scope_iam_role = set_role(
              principal_to_roles[iam_member].scope_iam_role, scope_iam_role
          )
          if ',' in principal_to_roles[iam_member].scope_iam_role:
            principal_to_roles[iam_member].overall_role = 'custom'

  for iam_member in principal_to_roles:
    if not scopes_util.RbacAndScopeIamRolesMatch(
        principal_to_roles[iam_member].scope_rrb_role,
        principal_to_roles[iam_member].scope_iam_role,
    ):
      principal_to_roles[iam_member].overall_role = 'custom'


def derive_log_view_access_role(
    project_iam_policy, condition, principal_to_roles
):
  """Derive the conditional log view access role for the principals in the given project IAM policy."""
  # Find IAM members associated with the scope through conditional bindings
  # (bucket == scope) to the log view access role.
  for binding in project_iam_policy.bindings:
    if binding.role != 'roles/logging.viewAccessor':
      continue
    # Condition expression specifies the bucket for the scope.
    if condition.get('expression') != binding.condition.expression:
      continue
    for iam_member in binding.members:
      if iam_member not in principal_to_roles:
        init_principal(principal_to_roles, iam_member)
      principal_to_roles[iam_member].log_view_access = 'granted'

  for iam_member in principal_to_roles:
    if principal_to_roles[iam_member].log_view_access != 'granted':
      principal_to_roles[iam_member].overall_role = 'custom'


def find_project_level_iam_role(project_iam_policy, principal_to_roles):
  """Derive the project-level IAM role for the principals in the given project IAM policy."""
  for iam_member in principal_to_roles:
    if principal_to_roles[iam_member].overall_role == 'custom':
      # Show all existing project-level IAM scope roles because we don't know
      # which one is relevant.
      for project_iam_role in scopes_util.AllIamProjectLevelScopeRoles():
        if iam_util.BindingInPolicy(
            project_iam_policy, iam_member, project_iam_role
        ):
          principal_to_roles[iam_member].project_iam_role = set_role(
              principal_to_roles[iam_member].project_iam_role, project_iam_role
          )
    else:
      # Show only the relevant project-level IAM role (if it exists).
      project_iam_role = scopes_util.IamProjectLevelScopeRoleFromRbac(
          principal_to_roles[iam_member].overall_role
      )
      if iam_util.BindingInPolicy(
          project_iam_policy, iam_member, project_iam_role
      ):
        principal_to_roles[iam_member].project_iam_role = project_iam_role
      else:
        principal_to_roles[iam_member].overall_role = 'custom'


def finalize_roles(
    principal_to_roles,
    has_scope_rrb_permission,
    has_scope_iam_permission,
    has_project_iam_permission,
):
  """Finalize the roles in case of permission denied errors."""
  for iam_member in principal_to_roles:
    if not has_scope_rrb_permission:
      principal_to_roles[iam_member].scope_rrb_role = 'permission denied'
      principal_to_roles[iam_member].overall_role = 'unknown'
    if not has_scope_iam_permission:
      principal_to_roles[iam_member].scope_iam_role = 'permission denied'
      principal_to_roles[iam_member].overall_role = 'unknown'
    if not has_project_iam_permission:
      principal_to_roles[iam_member].project_iam_role = 'permission denied'
      principal_to_roles[iam_member].log_view_access = 'permission denied'
      principal_to_roles[iam_member].overall_role = 'unknown'


def init_principal(principal_to_roles, iam_member):
  principal_to_roles[iam_member] = scopes_util.AppOperatorBinding(
      principal=iam_member,
      overall_role='custom',
      scope_rrb_role='not found',
      scope_iam_role='not found',
      project_iam_role='not found',
      log_view_access='not found',
  )


def set_role(existing_role, new_role):
  if existing_role == 'not found':
    return new_role
  if new_role in existing_role:
    return existing_role
  return existing_role + ',' + new_role
