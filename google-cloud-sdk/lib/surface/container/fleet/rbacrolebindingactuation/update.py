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
"""The command to update the RbacRoleBinding Actuation Feature."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet.features import base as feature_base
from googlecloudsdk.command_lib.util.apis import arg_utils

RBACROLEBINDING_ACTUATION_FEATURE = 'rbacrolebindingactuation'


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Update(feature_base.UpdateCommand):
  r"""Update RbacRoleBinding Actuation Feature.

  This command updates RbacRoleBinding Actuation Feature in a fleet.

  ## EXAMPLES

  To update the RbacRoleBinding Actuation Feature, run:

    $ gcloud container fleet rbacrolebinding-actuation update \
        --allowed-custom-roles=role1,role2

    $ gcloud container fleet rbacrolebinding-actuation update \
        --add-allowed-custom-role=role1

    $ gcloud container fleet rbacrolebinding-actuation update \
        --remove-allowed-custom-role=role2
  """

  feature_name = 'rbacrolebindingactuation'

  @classmethod
  def Args(cls, parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--allowed-custom-roles',
        type=arg_parsers.ArgList(),
        metavar='ROLES',
        help=textwrap.dedent("""\
          The list of allowed custom roles that can be used in scope
          RBACRoleBindings.
          """),
    )
    group.add_argument(
        '--add-allowed-custom-role',
        type=str,
        help='Add a single custom role to the allowed custom roles list.',
    )
    group.add_argument(
        '--remove-allowed-custom-role',
        type=str,
        help='Remove a single custom role from the allowed custom roles list.',
    )

  def Run(self, args):
    project = arg_utils.GetFromNamespace(args, '--project', use_defaults=True)
    enable_cmd = _EnableCommand(args)
    feature = enable_cmd.GetWithForceEnable(project)
    self.Update(feature, args)

  def Update(self, feature, args):
    """Updates RbacRoleBinding Actuation Feature information for a fleet."""
    rrb_feature = self.GetFeature()
    current_custom_roles = (
        rrb_feature.spec.rbacrolebindingactuation.allowedCustomRoles
    )
    if args.allowed_custom_roles is not None:
      updated_custom_roles = args.allowed_custom_roles
    elif args.add_allowed_custom_role is not None:
      current_custom_roles.append(args.add_allowed_custom_role)
      updated_custom_roles = current_custom_roles
    elif args.remove_allowed_custom_role is not None:
      updated_custom_roles = [
          role
          for role in current_custom_roles
          if role != args.remove_allowed_custom_role
      ]
    else:
      raise ValueError(
          'One of --allowed-custom-roles, --add-allowed-custom-role, or'
          ' --remove-allowed-custom-role must be specified.'
      )

    patch = self.messages.Feature(
        spec=self.messages.CommonFeatureSpec(
            rbacrolebindingactuation=self.messages.RBACRoleBindingActuationFeatureSpec(
                allowedCustomRoles=updated_custom_roles,
            ),
        )
    )
    path = 'spec.rbacrolebindingactuation.allowed_custom_roles'
    return super(Update, self).Update([path], patch)


class _EnableCommand(feature_base.EnableCommandMixin):
  """Base class for enabling the RBACRoleBinding Actuation Feature."""

  def __init__(self, args):
    self.feature_name = RBACROLEBINDING_ACTUATION_FEATURE
    self.args = args

  def ReleaseTrack(self):
    """Required to initialize HubClient. See calliope base class."""
    return self.args.calliope_command.ReleaseTrack()

  def GetWithForceEnable(self, project):
    """Gets the project's Cluster Upgrade Feature, enabling if necessary."""
    try:
      # Get the feature without transforming HTTP errors.
      return self.hubclient.GetFeature(
          self.FeatureResourceName(project=project)
      )
    except apitools_exceptions.HttpNotFoundError:
      # It is expected for self.GetFeature to raise an exception when the
      # feature is not enabled. If that is the case, we enable it on behalf of
      # the caller.
      self.Enable(self.messages.Feature())
      return self.GetFeature()
