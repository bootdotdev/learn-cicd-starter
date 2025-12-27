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
"""Command to simulate orgpolicy."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding_helper
from apitools.base.py import list_pager
from googlecloudsdk.api_lib.orgpolicy import utils as orgpolicy_utils
from googlecloudsdk.api_lib.policy_intelligence import orgpolicy_simulator
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.policy_intelligence.simulator.orgpolicy import utils
from googlecloudsdk.core import log


_DETAILED_HELP = {
    'brief':
        """\
      Understand how changes to organization policies could affect your
      resources.
        """,
    'DESCRIPTION':
        """\
      Understand how changes to organization policies could affect your
      resources.
        """,
    'EXAMPLES':
        """\
      To simulate changes to custom constraints defined in
      `./custom-constraint.json`, run:

        $ {command}
        --organization=ORGANIZATION_ID
        --custom-constraints=custom-constraint.json

      To simulate changes to organization policies defined in `./policy.json`,
      run:

        $ {command}
        --organization=ORGANIZATION_ID
        --policies=policy.json

      To simulate changes to both custom constraints defined in
      `./custom-constraint.json` and organization policies defined in
      `./policy.json`, run:

        $ {command}
        --organization=ORGANIZATION_ID
        --policies=policy.json
        --custom-constraints=custom-constraint.json

      See https://cloud.google.com/policy-intelligence/docs/test-organization-policies
      for more information about Policy Simulator for Organization Policy.

      """
}


def _ArgsParse(parser):
  """Parses arguments for the commands."""
  parser.add_argument(
      '--organization',
      metavar='ORGANIZATION_ID',
      required=True,
      help=('Organization ID.'))

  parser.add_argument(
      '--policies',
      type=arg_parsers.ArgList(),
      metavar='POLICIES',
      action=arg_parsers.UpdateAction,
      help="""Path to the JSON or YAML file that contains the organization
      policy to simulate. Multiple policies can be simulated by providing
      multiple, comma-separated paths. For example: `--policies=p1.json,p2.json`
      """)

  parser.add_argument(
      '--custom-constraints',
      type=arg_parsers.ArgList(),
      metavar='CUSTOM_CONSTRAINTS',
      action=arg_parsers.UpdateAction,
      help="""Path to the JSON or YAML file that contains the custom constraints
      to simulate. Multiple custom constraints can be simulated by providing
      multiple, comma-separated paths. For example:
      `--custom-constraints=constraint1.json,constraint2.json`
      """)


def _Run(args, version):
  """Run the workflow for Policy Simulator for Organization Policy."""
  if not args.policies and not args.custom_constraints:
    raise exceptions.ConflictingArgumentsException(
        'Must specify either `--policies`, `--custom-constraints`, or both.')
  op_api = orgpolicy_simulator.OrgPolicySimulatorApi(
      version)

  # Parse files and get Policy Overlay
  policies = []
  if args.policies:
    for policy_file in args.policies:
      policy = utils.GetPolicyMessageFromFile(policy_file,
                                              version)
      if not policy.name:
        raise exceptions.InvalidArgumentException(
            'Policy name',
            "'name' field not present in the organization policy.")
      policy_parent = orgpolicy_utils.GetResourceFromPolicyName(
          policy.name)
      policy_overlay = op_api.GetOrgPolicyPolicyOverlay(
          policy=policy,
          policy_parent=policy_parent)
      policies.append(policy_overlay)

  # Parse files and get Custom Constraints Overlay
  custom_constraints = []
  if args.custom_constraints:
    for custom_constraint_file in args.custom_constraints:
      custom_constraint = utils.GetCustomConstraintMessageFromFile(
          custom_constraint_file,
          version)
      if not custom_constraint.name:
        raise exceptions.InvalidArgumentException(
            'Custom constraint name',
            "'name' field not present in the custom constraint.")
      custom_constraint_parent = orgpolicy_utils.GetResourceFromPolicyName(
          custom_constraint.name)
      constraint_overlay = op_api.GetOrgPolicyCustomConstraintOverlay(
          custom_constraint=custom_constraint,
          custom_constraint_parent=custom_constraint_parent)
      custom_constraints.append(constraint_overlay)

  overlay = op_api.GetOrgPolicyOverlay(
      policies=policies, custom_constraints=custom_constraints)

  # Create Violations Preview and get long operation id
  organization_resource = 'organizations/' + args.organization
  parent = utils.GetParentFromOrganization(organization_resource)
  violations = op_api.GetPolicysimulatorOrgPolicyViolationsPreview(
      overlay=overlay)
  request = op_api.CreateOrgPolicyViolationsPreviewRequest(
      violations_preview=violations,
      parent=parent)
  op_service = op_api.client.OrganizationsLocationsOrgPolicyViolationsPreviewsService(
      op_api.client)
  violations_preview_operation = op_service.Create(
      request=request)

  # Poll Long Running Operation and get Violations Preview
  operation_response_raw = op_api.WaitForOperation(
      violations_preview_operation,
      'Waiting for operation [{}] to complete'.format(
          violations_preview_operation.name))

  preview = encoding_helper.JsonToMessage(
      op_api.GetOrgPolicyViolationsPreviewMessage(),
      encoding_helper.MessageToJson(operation_response_raw))

  if not preview.violationsCount or not preview.resourceCounts:
    log.err.Print('No violations found in the violations preview.\n')

  # List results of the Violations under Violations Preview.
  list_violations_request = op_api.messages.PolicysimulatorOrganizationsLocationsOrgPolicyViolationsPreviewsOrgPolicyViolationsListRequest(
      parent=preview.name)
  pov_service = op_api.client.OrganizationsLocationsOrgPolicyViolationsPreviewsOrgPolicyViolationsService(
      op_api.client)

  return list_pager.YieldFromList(
      pov_service,
      list_violations_request,
      batch_size=1000,
      field='orgPolicyViolations',
      batch_size_attribute='pageSize')


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class SimulateAlpha(base.Command):
  """Simulate changes to organization policies."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Parses arguments for the commands."""
    _ArgsParse(parser)

  def Run(self, args):
    return _Run(args, self.ReleaseTrack())


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class SimulateBeta(base.Command):
  """Simulate changes to organization policies."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Parses arguments for the commands."""
    _ArgsParse(parser)

  def Run(self, args):
    return _Run(args, self.ReleaseTrack())


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class SimulateGA(base.Command):
  """Simulate changes to organization policies."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Parses arguments for the commands."""
    _ArgsParse(parser)

  def Run(self, args):
    return _Run(args, self.ReleaseTrack())
