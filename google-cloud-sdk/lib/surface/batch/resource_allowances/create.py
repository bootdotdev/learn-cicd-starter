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
"""Command to create a specified Batch resource allowance."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.protorpclite.messages import DecodeError
from apitools.base.py import encoding
from googlecloudsdk.api_lib.batch import resource_allowances
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.batch import resource_args
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml


@base.DefaultUniverseOnly
class Submit(base.Command):
  """Create a Batch resource allowance.

  This command creates a Batch resource allowance.

  ## EXAMPLES

  The following command submit a resource allowance with config.json sample
  config file
  `projects/foo/locations/us-central1/resousrceAllowances/bar`:

    $ {command} projects/foo/locations/us-central1/resousrceAllowances/bar
    --config config.json
  """

  @staticmethod
  def Args(parser):
    resource_args.AddCreateResourceAllowanceResourceArgs(parser)

    parser.add_argument(
        '--config',
        type=arg_parsers.FileContents(),
        required=True,
        help="""The config file of a resource allowance.""",
    )

  @classmethod
  def _CreateResourceAllowanceMessage(cls, batch_msgs, config):
    """Parse into ResourceAllowance message using the config input.

    Args:
         batch_msgs: Batch defined proto message.
         config: The input content being either YAML or JSON or the HEREDOC
           input.

    Returns:
         The Parsed resource allowance message.
    """
    try:
      result = encoding.PyValueToMessage(
          batch_msgs.ResourceAllowance, yaml.load(config)
      )
    except (ValueError, AttributeError, yaml.YAMLParseError):
      try:
        result = encoding.JsonToMessage(batch_msgs.ResourceAllowance, config)
      except (ValueError, DecodeError) as e:
        raise exceptions.Error('Unable to parse config file: {}'.format(e))
    return result

  def Run(self, args):
    resource_allowance_ref = args.CONCEPTS.resource_allowance.Parse()
    location_ref = resource_allowance_ref.Parent()
    resource_allowance_id = resource_allowance_ref.RelativeName().split('/')[-1]

    # Remove the invalid resource_allowance_id if no resource_allowance_id
    # being specified, batch_client would create a valid job_id.
    if resource_allowance_id == resource_args.INVALIDID:
      resource_allowance_id = None

    release_track = self.ReleaseTrack()

    batch_client = resource_allowances.ResourceAllowancesClient(release_track)
    batch_msgs = batch_client.messages
    resource_allowance_msg = batch_msgs.ResourceAllowance()

    if args.config:
      resource_allowance_msg = self._CreateResourceAllowanceMessage(
          batch_msgs, args.config
      )

    resp = batch_client.Create(
        resource_allowance_id, location_ref, resource_allowance_msg
    )
    log.status.Print(
        'ResourceAllowance {resourceAllowanceName} was successfully created.'
        .format(resourceAllowanceName=resp.uid)
    )
    return resp
