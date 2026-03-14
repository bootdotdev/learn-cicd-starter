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
"""Command for configuring strict priority policy for application awareness on interconnect."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects import flags


DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to configure strict priority policy for using
        application awareness on interconnect.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To configure strict priority policy for an interconnect
        example-interconnect, run:

          $ {command} example-interconnect
          --enabled --profile-description="some string"
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ConfigureStrictPriorityPolicy(base.UpdateCommand):
  """Configure strict priority policy for application awareness configuration of a Compute Engine interconnect.

  *{command}* allows the user to configure strict priority policy for
  application awareness configuration data associated with
  Compute Engine interconnect in a project.
  """

  INTERCONNECT_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_ARG = flags.InterconnectArgument()
    cls.INTERCONNECT_ARG.AddArgument(parser, operation_type='patch')

    flags.AddAaiEnabled(parser)
    flags.AddAaiProfileDescription(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_ARG.ResolveAsResource(args, holder.resources)
    interconnect = client.Interconnect(ref, compute_client=holder.client)

    # Get the current object for application awareness
    application_awareness = interconnect.Describe().applicationAwareInterconnect

    if application_awareness is None:
      application_awareness = (
          holder.client.messages.InterconnectApplicationAwareInterconnect()
      )

    if application_awareness.strictPriorityPolicy is None:
      application_awareness.strictPriorityPolicy = (
          holder.client.messages.InterconnectApplicationAwareInterconnectStrictPriorityPolicy()
      )
    application_awareness.bandwidthPercentagePolicy = None

    application_awareness.profileDescription = args.profile_description

    enabled = args.enabled
    # Enable the policy by default if not explicity specified.
    if args.enabled is None:
      enabled = True

    return interconnect.Patch(
        description=None,
        interconnect_type=None,
        requested_link_count=None,
        link_type=None,
        admin_enabled=None,
        noc_contact_email=None,
        location=None,
        labels=None,
        label_fingerprint=None,
        macsec_enabled=None,
        macsec=None,
        aai_enabled=enabled,
        application_aware_interconnect=application_awareness,
    )


ConfigureStrictPriorityPolicy.detailed_help = DETAILED_HELP
