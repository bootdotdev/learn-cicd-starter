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
"""Command to delete the specified Kafka source."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import kafka_sources
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.core.console import console_io

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To delete the Kafka source `my-kafka-source` in location `us-central1`, run:

          $ {command} my-kafka-source --location=us-central1
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class Delete(base.DeleteCommand):
  """Delete an Eventarc Kafka source."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddKafkaSourceResourceArg(
        parser, 'Kafka source to delete.', required=True
    )
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the delete command."""
    client = kafka_sources.KafkaSourceClientV1()
    kafka_source_ref = args.CONCEPTS.kafka_source.Parse()

    console_io.PromptContinue(
        message=(
            'The following Kafka source will be deleted.\n'
            '[{name}] in location [{location}]'.format(
                name=kafka_source_ref.kafkaSourcesId,
                location=kafka_source_ref.locationsId,
            )
        ),
        throw_if_unattended=True,
        cancel_on_no=True,
    )
    operation = client.Delete(kafka_source_ref)

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Deleting', kafka_source_ref)
