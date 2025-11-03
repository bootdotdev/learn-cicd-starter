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
"""Command for configuring bandwidth percentage policy for application awareness on interconnect."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects import flags

DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to configure bandwidth percentage policy for using
        application awareness on interconnect.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To configure bandwidth percentage policy for an interconnect
        example-interconnect, run:

          $ {command} example-interconnect
          --bandwidth-percentages="TC1=5,TC2=5,TC3=75,TC4=5,TC5=5,TC6=5"
          --enabled --profile-description="some string"
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class ConfigureBandwidthPercentagePolicy(base.UpdateCommand):
  """Configure bandwidth percentage policy for application awareness configuration of a Compute Engine interconnect.

  *{command}* allows the user to configure bandwidth percentage policy for
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

    if application_awareness is None:
      application_awareness = (
          messages.InterconnectApplicationAwareInterconnect()
      )

    aai_enabled = args.enabled
    # Enable the policy by default if not explicity specified.
    if aai_enabled is None:
      aai_enabled = True
    application_awareness.strictPriorityPolicy = None
    application_awareness.profileDescription = args.profile_description

    application_awareness.bandwidthPercentagePolicy = (
        messages.InterconnectApplicationAwareInterconnectBandwidthPercentagePolicy()
    )

    aai_bandwidth_percentages = flags.GetAaiBandwidthPercentages(
        messages, args.bandwidth_percentages
    )

    for traffic_class in aai_bandwidth_percentages:
      application_awareness.bandwidthPercentagePolicy.bandwidthPercentages.append(
          messages.InterconnectApplicationAwareInterconnectBandwidthPercentage(
              percentage=aai_bandwidth_percentages[traffic_class],
              trafficClass=traffic_class,
          )
      )

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
        aai_enabled=aai_enabled,
        application_aware_interconnect=application_awareness,
    )


ConfigureBandwidthPercentagePolicy.detailed_help = DETAILED_HELP
