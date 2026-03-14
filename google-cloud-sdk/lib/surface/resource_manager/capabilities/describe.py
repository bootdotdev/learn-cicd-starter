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
"""Command to show metadata for a specified capability."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.resource_manager import capabilities
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.resource_manager import flags


@base.Hidden
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Show whether a Capability is enabled.

  Command to show whether a Capability is enabled.

  This command can fail for the following reasons:
      * The capability specified does not exist.
      * The active account does not have permission to access the given
        folder/capability.

  ## EXAMPLES

  The following command prints metadata for a capability with the ID
  `folders/123/capabilities/app-management`:

    $ {command} "folders/123/capabilities/app-management"
  """

  @staticmethod
  def Args(parser):
    flags.CapabilityIdArg('you want to describe.').AddToParser(parser)

  def Run(self, args):
    return capabilities.GetCapability(args.id)
