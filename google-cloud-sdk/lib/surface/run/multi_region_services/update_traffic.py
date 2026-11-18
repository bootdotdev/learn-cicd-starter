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
"""Command for updating env vars and other configuration info."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import platforms
from surface.run.services import update_traffic


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class MultiRegionAdjustTraffic(update_traffic.AdjustTraffic):
  """Adjust the traffic assignments for a Cloud Run Multi-Region service."""

  def IsMultiRegion(self):
    return True

  @classmethod
  def Args(cls, parser):
    update_traffic.AdjustTraffic.Args(parser)

  def Run(self, args):
    if platforms.GetPlatform() != platforms.PLATFORM_MANAGED:
      raise c_exceptions.InvalidArgumentException(
          '--platform',
          'Multi-region Services are only supported on managed platform.',
      )
    if flags.FlagIsExplicitlySet(args, 'region'):
      raise c_exceptions.InvalidArgumentException(
          '--region',
          'Multi-region Services do not support the --region flag.',
      )
    # TODO(b/449850649): Remove after propagating tags in the mixer.
    if flags.FlagIsExplicitlySet(args, 'to_tags'):
      raise c_exceptions.InvalidArgumentException(
          '--to-tags',
          'Multi-region Services do not currently support tags. Please check'
          ' back soon.',
      )
    if (
        flags.FlagIsExplicitlySet(args, 'set_tags')
        or flags.FlagIsExplicitlySet(args, 'remove_tags')
        or flags.FlagIsExplicitlySet(args, 'update_tags')
    ):
      raise c_exceptions.InvalidArgumentException(
          'tags',
          'Multi-region Services do not currently support tags. Please check'
          ' back soon.',
      )
    return update_traffic.AdjustTraffic.Run(self, args)
