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
"""Create command to create a new resource of Custom Mirroring profile."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.security_profiles import mirroring_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import endpoint_group_association_flags as mirroring_flags
from googlecloudsdk.command_lib.network_security import sp_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log

DETAILED_HELP = {
    'DESCRIPTION': """

          Create a new Custom Mirroring Security Profile.

        """,
    'EXAMPLES': """
          To create a Custom Mirroring Security Profile named `mirroring-profile` linked to a Mirroring Endpoint Group (q.v.), run:

              $ {command} mirroring-profile --description="A Mirroring Profile" \
                --mirroring-endpoint-group=projects/my-project/locations/global/mirroringEndpointGroups/my-mep

        """,
}

_BROKER_RELEASE_TRACKS = (base.ReleaseTrack.ALPHA,)


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Create(base.CreateCommand):
  """Create a new Custom Mirroring Profile."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    sp_flags.AddSecurityProfileResource(parser, cls.ReleaseTrack())
    sp_flags.AddProfileDescription(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)
    labels_util.AddCreateLabelsFlags(parser)
    mirroring_flags.AddMirroringEndpointGroupResource(
        cls.ReleaseTrack(), parser
    )
    if cls.ReleaseTrack() in _BROKER_RELEASE_TRACKS:
      sp_flags.AddCustomMirroringDeploymentGroupsArg(parser)

  def Run(self, args):
    client = mirroring_api.Client(self.ReleaseTrack())
    security_profile = args.CONCEPTS.security_profile.Parse()
    description = args.description
    labels = labels_util.ParseCreateArgs(
        args, client.messages.SecurityProfile.LabelsValue
    )
    is_async = args.async_
    mirroring_endpoint_group = args.CONCEPTS.mirroring_endpoint_group.Parse()

    mirroring_deployment_groups = None
    if self.ReleaseTrack() in _BROKER_RELEASE_TRACKS:
      mirroring_deployment_groups = args.mirroring_deployment_groups

    if args.location != 'global':
      raise core_exceptions.Error(
          'Only `global` location is supported, but got: %s' % args.location
      )

    response = client.CreateCustomMirroringProfile(
        sp_id=security_profile.Name(),
        parent=security_profile.Parent().RelativeName(),
        description=description,
        labels=labels,
        mirroring_endpoint_group=mirroring_endpoint_group.RelativeName(),
        mirroring_deployment_groups=mirroring_deployment_groups,
    )

    # Return the in-progress operation if async is requested.
    if is_async:
      operation_id = response.name
      log.status.Print(
          'Check for operation completion status using operation ID:',
          operation_id,
      )
      return response

    # Default operation poller if async is not specified.
    return client.WaitForOperation(
        operation_ref=client.GetOperationsRef(response),
        message='Waiting for security-profile [{}] to be created'.format(
            security_profile.RelativeName()
        ),
        has_result=True,
    )
