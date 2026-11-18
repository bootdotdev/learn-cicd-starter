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
"""Command for deleting configuration for application awareness on interconnect."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.interconnects import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.interconnects import flags


DETAILED_HELP = {
    'DESCRIPTION': """\
        *{command}* is used to delete all configuration state for
        application awareness on interconnect.

        For an example, refer to the *EXAMPLES* section below.
        """,
    'EXAMPLES': """\
        To delete application awareness configuration for an interconnect
        example-interconnect, run:

          $ {command} example-interconnect
        """,
}


@base.UniverseCompatible
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Delete(base.UpdateCommand):
  """Delete application awareness configuration of a Compute Engine interconnect.

  *{command}* allows the user to delete application awareness configuration data
  associated with
  Compute Engine interconnect in a project.
  """

  INTERCONNECT_ARG = None

  @classmethod
  def Args(cls, parser):
    cls.INTERCONNECT_ARG = flags.InterconnectArgument()
    cls.INTERCONNECT_ARG.AddArgument(parser, operation_type='patch')

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    ref = self.INTERCONNECT_ARG.ResolveAsResource(args, holder.resources)
    interconnect = client.Interconnect(ref, compute_client=holder.client)
    messages = holder.client.messages

    application_awareness = messages.InterconnectApplicationAwareInterconnect()
    cleared_fields = [
        'applicationAwareInterconnect.shapeAveragePercentages',
        'applicationAwareInterconnect.bandwidthPercentagePolicy',
        'applicationAwareInterconnect.strictPriorityPolicy',
    ]
    application_awareness.strictPriorityPolicy = None
    application_awareness.bandwidthPercentagePolicy = None
    application_awareness.profileDescription = ''
    application_awareness.shapeAveragePercentages = []

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
        aai_enabled=False,
        application_aware_interconnect=application_awareness,
        cleared_fields=cleared_fields,
    )


Delete.detailed_help = DETAILED_HELP
