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
"""Command to update a folder capability."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.resource_manager import capabilities
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.resource_manager import flags


@base.Hidden
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class Update(base.Command):
  """Update a folder capability.

  Command to Update/Set the `value` field of the Folder capability. This
  can be done by using the `--enable` flag to set the value to True, and
  the `--no-enable` flag to set the value to False.

  This command can fail for the following reasons:
      * There is no folder parenting the given capability name.
      * The active account does not have permission to update the given
        folder/capability.

  ## EXAMPLES

  The following command updates a capability with the ID
  `folders/123/capabilities/app-management` to have
  the value True:

    $ {command} "folders/123/capabilities/app-management" --enable

  In order to set the value to False, the following command can be used:

    $ {command} "folders/123/capabilities/app-management" --no-enable
  """

  @staticmethod
  def Args(parser):
    flags.CapabilityIdArg('you want to update.').AddToParser(parser)
    parser.add_argument(
        '--enable',
        action=arg_parsers.StoreTrueFalseAction,
        dest='value',
        required=True,
        help='Enable the Capability',
    )
    parser.add_argument(
        '--update-mask',
        help=(
            'Update Mask. This is an optional field, and the only valid value'
            ' this can be set to currently is "value".'
        ),
    )

  def Run(self, args):
    capability_name = args.id
    return capabilities.UpdateCapability(
        capability_name, args.value, args.update_mask
    )
