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
"""The command group for Cloud Run presets."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import platforms


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class Presets(base.Group):
  """View available Cloud Run service presets.

  This command group allows you to list available presets for Cloud Run
  services.
  """

  detailed_help = {
      'DESCRIPTION': """
          This command group allows you to list and describe presets for your
          Cloud Run services.
          """,
      'EXAMPLES': """
          To list all available presets, run:

            $ {command} list

          To get detailed information about a specific preset, run:

            $ {command} describe <preset-name>
      """,
  }

  def Filter(self, context, args):
    """Runs before command.Run and validates platform with passed args."""
    flags.GetAndValidatePlatform(
        args, self.ReleaseTrack(), flags.Product.RUN)

  @staticmethod
  def Args(parser):
    """Adds --platform and the various related args."""
    flags.AddPlatformAndLocationFlags(parser)
