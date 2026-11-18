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
"""The gcloud run multi-region-services group."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import flags

DETAILED_HELP = {
    'brief': 'Manage your Cloud Run multi-region services.',
    'DESCRIPTION': """
        The gcloud run multi-region-services command group lets you deploy container images
        to Google Cloud Run across multiple regions at once.
        """,
    'EXAMPLES': """
        To deploy your container, use the `gcloud run multi-region-services deploy` command:

          $ {command} deploy <service-name> --image <image_name> --regions [region-list]
        For more information, run:
          $ gcloud run deploy --help
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA,
                    base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class MultiRegionServices(base.Group):
  """Manage your Cloud Run resources."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Adds --platform and the various related args."""
    flags.AddPlatformAndLocationFlags(parser)

  def Filter(self, context, args):
    """Runs before any commands in this group."""
    # TODO(b/190539410):  Determine if command group works with project number
    base.RequireProjectID(args)
    del context, args
