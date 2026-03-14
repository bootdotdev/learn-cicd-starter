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
"""Command to update a specified Batch resource allowance."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.batch import resource_allowances
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.batch import resource_args
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
class Update(base.Command):
  """Update a Batch resource allowance.

  This command updates a Batch resource allowance.

  ## EXAMPLES

  The following command updates a resource allowance limit to 0
  `projects/foo/locations/us-central1/resousrceAllowances/bar`:

    $ {command} projects/foo/locations/us-central1/resousrceAllowances/bar
    --usage-limit 0
  """

  @staticmethod
  def Args(parser):
    resource_args.AddResourceAllowanceResourceArgs(parser)

    parser.add_argument(
        '--usage-limit',
        help="""Limit value of a UsageResourceAllowance within its one
      duration. Limit cannot be a negative value. Default is 0.""",
    )

  def Run(self, args):
    update_mask = self.GenerateUpdateMask(args)
    if len(update_mask) < 1:
      raise exceptions.Error(
          'Update commands must specify at least one additional parameter to'
          ' change.'
      )

    release_track = self.ReleaseTrack()
    batch_client = resource_allowances.ResourceAllowancesClient(release_track)
    resource_allowance_ref = args.CONCEPTS.resource_allowance.Parse()
    batch_msgs = batch_client.messages
    resource_allowance_msg = batch_msgs.ResourceAllowance()
    if args.IsSpecified('usage_limit'):
      setattr(
          resource_allowance_msg,
          'usageResourceAllowance',
          batch_msgs.UsageResourceAllowance(
              spec=(
                  batch_msgs.UsageResourceAllowanceSpec(
                      limit=batch_msgs.Limit(
                          limit=float(args.usage_limit)
                      )
                  )
              )
          ),
      )
    resp = batch_client.Update(
        resource_allowance_ref, resource_allowance_msg, update_mask
    )
    log.status.Print(
        'ResourceAllowance {resourceAllowanceName} was successfully updated.'
        .format(resourceAllowanceName=resp.uid)
    )
    return resp

  def GenerateUpdateMask(self, args):
    """Create Update Mask for ResourceAllowances."""
    update_mask = []
    if args.IsSpecified('usage_limit'):
      update_mask.append('usageResourceAllowance.spec.limit.limit')
    return update_mask
