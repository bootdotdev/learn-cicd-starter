# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Implements command to delete an ops agents policy."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import encoding
from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.compute.instances.ops_agents import cloud_ops_agents_util
from googlecloudsdk.api_lib.compute.instances.ops_agents import exceptions as ops_agents_exceptions
from googlecloudsdk.api_lib.compute.instances.ops_agents.converters import os_policy_assignment_to_cloud_ops_agents_policy_converter as to_ops_agents_policy
from googlecloudsdk.api_lib.compute.instances.ops_agents.validators import guest_policy_validator
from googlecloudsdk.api_lib.compute.os_config import utils as osconfig_api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.instances.ops_agents.policies import parser_utils
from googlecloudsdk.command_lib.compute.os_config import utils as osconfig_command_utils
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.generated_clients.apis.osconfig.v1 import osconfig_v1_messages as osconfig


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA)
class DeleteAlphaBeta(base.DeleteCommand):
  """Delete a Google Cloud's operations suite agents (Ops Agents) policy.

  *{command}* deletes a policy that facilitates agent management across
  Compute Engine instances based on user specified instance filters. This policy
  installs, specifies versioning, enables autoupgrade, and removes Ops Agents.

  The command returns a response indicating whether the deletion succeeded.
  After a policy is deleted, it takes 10-15 minutes to be wiped from the
  applicable instances. Deleting a policy does not delete any existing agents
  managed by that policy, but the agents become unmanaged by any policies. To
  remove the agents from the
  instances, first update the policy to set the agent ``package-state'' to
  ``removed'', wait for the policy to take effect, then delete the policy.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          To delete an Ops agents policy named ``ops-agents-test-policy'' in the
          current project, run:

            $ {command} ops-agents-test-policy
          """,
  }

  @staticmethod
  def Args(parser):
    """See base class."""
    parser_utils.AddSharedArgs(parser)

  def Run(self, args):
    """See base class."""
    release_track = self.ReleaseTrack()
    client = osconfig_api_utils.GetClientInstance(
        release_track, api_version_override='v1beta'
    )
    messages = osconfig_api_utils.GetClientMessages(
        release_track, api_version_override='v1beta'
    )
    project = properties.VALUES.core.project.GetOrFail()
    guest_policy_uri_path = osconfig_command_utils.GetGuestPolicyUriPath(
        'projects', project, args.POLICY_ID
    )
    service = client.projects_guestPolicies

    get_request = messages.OsconfigProjectsGuestPoliciesGetRequest(
        name=guest_policy_uri_path
    )
    try:
      get_response = service.Get(get_request)
    except apitools_exceptions.HttpNotFoundError:
      raise ops_agents_exceptions.PolicyNotFoundError(policy_id=args.POLICY_ID)
    if not guest_policy_validator.IsOpsAgentPolicy(get_response):
      raise ops_agents_exceptions.PolicyNotFoundError(policy_id=args.POLICY_ID)

    delete_request = messages.OsconfigProjectsGuestPoliciesDeleteRequest(
        name=guest_policy_uri_path
    )
    delete_response = service.Delete(delete_request)

    log.DeletedResource(args.POLICY_ID)
    return delete_response


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Delete(base.Command):
  """Delete a Google Cloud Observability agents policy for the Ops Agent.

  *{command}* deletes a policy that facilitates agent management across
  Compute Engine instances based on user specified instance filters.

  The command returns a response indicating whether the deletion succeeded.
  After a policy is deleted, it takes 10-15 minutes to be wiped from the
  applicable instances. Deleting a policy does not delete any existing agents
  managed by that policy, but the agents become unmanaged by any policies. To
  remove the agents from the instances, first update the policy to set the
  agent ``packageState'' to ``removed'', wait for the policy to take effect,
  then delete the policy.

  The command returns the content of the deleted policy. For instance:

    agentsRule:
      packageState: installed
      version: latest
    instanceFilter:
      inclusionLabels:
      - labels:
          env: prod

  If no policies are found, or the policy is not an agents policy, then the
  command returns a ``NOT_FOUND'' error.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          To delete an agents policy named ``ops-agents-test-policy'' in the
          current project, run:

          $ {command} ops-agents-test-policy --zone=ZONE
          """,
  }

  @staticmethod
  def Args(parser):
    """See base class."""
    parser.add_argument(
        'POLICY_ID',
        type=str,
        help="""\
          ID of the policy.

          This ID must contain only lowercase letters,
          numbers, and hyphens, end with a number or a letter, be between 1-63
          characters, and be unique within the project.
          """,
    )
    parser.add_argument(
        '--zone',
        required=True,
        help="""\
          Zone of the agents policy you want to delete.""",
    )

  def Run(self, args):
    """See base class."""

    release_track = self.ReleaseTrack()
    project = properties.VALUES.core.project.GetOrFail()
    # Make sure the policy we're deleting is a valid Ops Agents policy.
    _ = cloud_ops_agents_util.GetOpsAgentsPolicyFromApi(
        release_track, args.POLICY_ID, project, args.zone
    )

    parent_path = osconfig_command_utils.GetProjectLocationUriPath(
        project, args.zone
    )

    assignment_id = osconfig_command_utils.GetOsPolicyAssignmentRelativePath(
        parent_path, args.POLICY_ID
    )

    messages = osconfig_api_utils.GetClientMessages(release_track)
    delete_request = (
        messages.OsconfigProjectsLocationsOsPolicyAssignmentsDeleteRequest(
            name=assignment_id
        )
    )

    client = osconfig_api_utils.GetClientInstance(release_track)
    service = client.projects_locations_osPolicyAssignments
    delete_response = service.Delete(delete_request)

    # Converting osconfig.Operation.ResponseValue to
    # osconfig.OSPolicyAssignment.
    delete_os_policy_assignment = encoding.PyValueToMessage(
        osconfig.OSPolicyAssignment,
        encoding.MessageToPyValue(delete_response.response),
    )
    ops_agents_policy = (
        to_ops_agents_policy.ConvertOsPolicyAssignmentToCloudOpsAgentsPolicy(
            delete_os_policy_assignment
        )
    )
    return ops_agents_policy.ToPyValue()
