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
"""Command for listing an organization posture deployments."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.scc.postures import util as securityposture_client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc import errors
from googlecloudsdk.command_lib.scc import util as scc_util
from googlecloudsdk.command_lib.scc.posture_deployments import flags


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List the details of the Cloud Security Command Center (SCC) posture deployments."""

  detailed_help = {
      "DESCRIPTION": """
          List the details of the Cloud Security Command Center (SCC) posture
          deployments for the specified organization.""",
      "EXAMPLES": """
          To list Cloud Security Command Center posture deployments for organization `123` in the `global` location, run:

            $ {command} organizations/123/locations/global

            $ {command} --organization=123 --location=global

            """,
      "API REFERENCE": (
          """
      This command uses the securityposture/v1 API. The full documentation for
    this API can be found at: https://cloud.google.com/security-command-center"""
      ),
  }

  @staticmethod
  def Args(parser):
    # Remove URI flag.
    base.URI_FLAG.RemoveFromParser(parser)

    # Add shared flags and parent positional argument.
    flags.AddParentOrFlagsGroup(parser)

  def Run(self, args):
    version = scc_util.GetVersionFromArguments(
        args, version_specific_existing_resource=True
    )

    messages = securityposture_client.GetMessagesModule(base.ReleaseTrack.GA)
    client = securityposture_client.GetClientInstance(base.ReleaseTrack.GA)

    location = scc_util.ValidateAndGetLocation(args, version)

    if (args.IsKnownAndSpecified("PARENT")) and (
        args.IsSpecified("organization") and args.IsSpecified("location")
    ):
      raise errors.InvalidSCCInputError(
          "Cannot provide both a positional `PARENT` and argument "
          "(`--organization`, `--location`) flags."
      )

    if (args.IsKnownAndSpecified("PARENT")):
      parent = args.PARENT
    elif (args.IsSpecified("organization") and args.IsSpecified("location")):
      parent = f"{scc_util.GetParentFromPositionalArguments(args)}/locations/{location}"
    else:
      raise errors.InvalidSCCInputError(
          "Must provide either positional `PARENT` or both `--organization` "
          "and `--location` flags."
      )

    # Build request.
    request = messages.SecuritypostureOrganizationsLocationsPostureDeploymentsListRequest(
        parent=parent,
        filter=getattr(args, "filter", None),
        pageSize=getattr(args, "page_size", None),
    )

    return list_pager.YieldFromList(
        client.organizations_locations_postureDeployments,
        request,
        batch_size_attribute="pageSize",
        batch_size=args.page_size,
        field="postureDeployments",
    )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class ListAlpha(base.ListCommand):
  """List the details of the Cloud Security Command Center (SCC) posture deployments."""

  detailed_help = {
      "DESCRIPTION": """
          List the details of the Cloud Security Command Center (SCC) posture
          deployments for the specified organization.""",
      "EXAMPLES": """
          To list Cloud Security Command Center posture deployments for organization `123` in the `global` location, run:

            $ {command} organizations/123/locations/global

            $ {command} --organization=123 --location=global

            """,
      "API REFERENCE": """
      This command uses the securityposture/v1alpha API. The full documentation for this API can be found at:
      https://cloud.google.com/security-command-center""",
  }

  @staticmethod
  def Args(parser):
    # Remove URI flag.
    base.URI_FLAG.RemoveFromParser(parser)

    # Add shared flags and parent positional argument.
    flags.AddParentOrFlagsGroup(parser)

  def Run(self, args):
    version = scc_util.GetVersionFromArguments(
        args, version_specific_existing_resource=True
    )

    messages = securityposture_client.GetMessagesModule(base.ReleaseTrack.ALPHA)
    client = securityposture_client.GetClientInstance(base.ReleaseTrack.ALPHA)

    location = scc_util.ValidateAndGetLocation(args, version)

    if (args.IsKnownAndSpecified("PARENT")) and (
        args.IsSpecified("organization") and args.IsSpecified("location")
    ):
      raise errors.InvalidSCCInputError(
          "Cannot provide both a positional `PARENT` and argument "
          "(`--organization`, `--location`) flags."
      )

    if (args.IsKnownAndSpecified("PARENT")):
      parent = args.PARENT
    elif (args.IsSpecified("organization") and args.IsSpecified("location")):
      parent = f"{scc_util.GetParentFromPositionalArguments(args)}/locations/{location}"
    else:
      raise errors.InvalidSCCInputError(
          "Must provide either positional `PARENT` or both `--organization` "
          "and `--location` flags."
      )

    # Build request.
    request = messages.SecuritypostureOrganizationsLocationsPostureDeploymentsListRequest(
        parent=parent,
        filter=getattr(args, "filter", None),
        pageSize=getattr(args, "page_size", None),
    )

    return list_pager.YieldFromList(
        client.organizations_locations_postureDeployments,
        request,
        batch_size_attribute="pageSize",
        batch_size=args.page_size,
        field="postureDeployments",
    )
