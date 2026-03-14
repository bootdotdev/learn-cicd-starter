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
"""Command for configuring shaper average percentage for application awareness on interconnect."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects import client
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute.interconnects import flags

DETAILED_HELP = {
    'DESCRIPTION': """\

        *{command}* is used to configure shaper average percentage for using
        application awareness on interconnect. Note that an application awareness
        policy (strict priority or bandwidth percentage) should be configure before
        configuring traffic shaping.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To configure shaper average percentage for an interconnect
        example-interconnect, run:

          $ {command} example-interconnect
          --bandwidth-percentages="TC1=30,TC2=90
          --enabled --profile-description="some string"
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ConfigureShaperAveragePercentage(base.UpdateCommand):
  """Configure shaper average percentage for application awareness configuration of a Compute Engine interconnect.

  *{command}* allows the user to configure shaper average percentage for
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
    flags.AddAaiBandwidthPercentages(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_ARG.ResolveAsResource(args, holder.resources)
    interconnect = client.Interconnect(ref, compute_client=holder.client)
    messages = holder.client.messages

    # Get the current object for application awareness
    application_awareness = interconnect.Describe().applicationAwareInterconnect

    # Raise an error.
    if (
        application_awareness is None
        or application_awareness
        == holder.client.messages.InterconnectApplicationAwareInterconnect()
    ):
      raise exceptions.BadArgumentException(
          'NAME',
          "Interconnect '{}' does not have application awareness configured."
          .format(ref.Name()),
      )

    aai_bandwidth_percentages = flags.GetAaiBandwidthPercentages(
        messages, args.bandwidth_percentages
    )

    application_awareness.profileDescription = args.profile_description

    application_awareness.shapeAveragePercentages = []
    for traffic_class in aai_bandwidth_percentages:
      application_awareness.shapeAveragePercentages.append(
          messages.InterconnectApplicationAwareInterconnectBandwidthPercentage(
              percentage=aai_bandwidth_percentages[traffic_class],
              trafficClass=traffic_class,
          )
      )

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


ConfigureShaperAveragePercentage.detailed_help = DETAILED_HELP
