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
"""Cloud Pub/Sub message transforms test command."""

from googlecloudsdk.api_lib.pubsub import message_transforms
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.pubsub import flags
from googlecloudsdk.command_lib.pubsub import util
from googlecloudsdk.core.util import http_encoding


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA
)
class Test(base.Command):
  """Tests message transforms against a given message."""

  @staticmethod
  def Args(parser):
    flags.AddTestMessageTransformFlags(parser)

  def Run(self, args):
    client = message_transforms.MessageTransformsClient()

    message_body = getattr(args, 'message', None)
    attributes = util.ParseAttributes(
        getattr(args, 'attribute', None), client.messages
    )
    message_transforms_file = getattr(args, 'message_transforms_file', None)
    topic = getattr(args, 'topic', None)
    if topic:
      topic = args.CONCEPTS.topic.Parse()
    subscription = getattr(args, 'subscription', None)
    if subscription:
      subscription = args.CONCEPTS.subscription.Parse()

    result = client.Test(
        project_ref=util.ParseProject(),
        message_body=http_encoding.Encode(message_body),
        attributes=attributes,
        message_transforms_file=message_transforms_file,
        topic_ref=topic,
        subscription_ref=subscription,
    )
    output = []
    for transformed_message in result.transformedMessages:
      if message := transformed_message.transformedMessage:
        message_copy = {}
        for field in message.all_fields():
          value = getattr(message, field.name)
          if value:
            if field.name == 'data':
              value = message.data.decode()
            message_copy[field.name] = value
        output.append(message_copy)
      else:
        output.append(transformed_message)
    return output
