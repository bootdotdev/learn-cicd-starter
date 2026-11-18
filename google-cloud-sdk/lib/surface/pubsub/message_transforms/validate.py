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
"""Cloud Pub/Sub message transforms validate command."""

from googlecloudsdk.api_lib.pubsub import message_transforms
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.pubsub import flags
from googlecloudsdk.command_lib.pubsub import util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class Validate(base.Command):
  """Validates a message transform."""

  @staticmethod
  def Args(parser):
    flags.AddValidateMessageTransformFlags(parser)

  def Run(self, args):
    client = message_transforms.MessageTransformsClient()

    message_transform_file = getattr(args, 'message_transform_file', None)

    client.Validate(util.ParseProject(), message_transform_file)
    log.status.Print('Message transform is valid.')
