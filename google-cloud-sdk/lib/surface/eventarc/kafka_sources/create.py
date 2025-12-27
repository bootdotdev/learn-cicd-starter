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
"""Command to create a Kafka source."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import kafka_sources
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To create a new Kafka source `my-kafka-source` in location `us-central1` with the required fields: bootstrap server URI 'https://example-cluster.com:9092', Kafka topics `topic1` and `topic2`, network attachment 'my-network-attachment', and message bus `my-message-bus`, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus

        To create a new Kafka source `my-kafka-source` in location `us-central1` with an initial offset of `newest`, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --initial-offset=newest

        To create a new Kafka source `my-kafka-source` in location `us-central1` with consumer group ID `my-kafka-source-group`, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --consumer-group-id=my-kafka-source-group

        To create a new Kafka source `my-kafka-source` in location `us-central1` SASL/Plain authentication with the Kafka broker, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --sasl-mechanism=PLAIN --sasl-username=kafka-username --sasl-password=projects/12345/secrets/my-sasl-secret/versions/1

        To create a new Kafka source `my-kafka-source` in location `us-central1` SASL/SCRAM-SHA-256 authentication with the Kafka broker, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --sasl-mechanism=SCRAM-SHA-256 --sasl-username=kafka-username --sasl-password=projects/12345/secrets/my-sasl-secret/versions/1

        To create a new Kafka source `my-kafka-source` in location `us-central1` SASL/SCRAM-SHA-512 authentication with the Kafka broker, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --sasl-mechanism=SCRAM-SHA-512 --sasl-username=kafka-username --sasl-password=projects/12345/secrets/my-sasl-secret/versions/1

        To create a new Kafka source `my-kafka-source` in location `us-central1` Mutual TLS (mTLS) authentication with the Kafka broker, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --tls-client-certificate=projects/12345/secrets/my-tls-cert/versions/1 --tls-client-key=projects/12345/secrets/my-tls-key/versions/1

        To create a new Kafka source `my-kafka-source` in location `us-central1` with an INFO level logging configuration, run:

          $ {command} my-kafka-source --location=us-central1 --bootstrap-servers='https://example-cluster.com:9092' --topics='topic1,topic2' --network_attachment=my-network-attachment --message-bus=my-message-bus --logging_config=INFO
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an Eventarc Kafka source."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddCreateKafkaSourceResourceArgs(parser)
    flags.AddKafkaSourceBootstrapServersArg(parser, required=True)
    flags.AddKafkaSourceTopicArg(parser, required=True)
    flags.AddKafkaSourceConsumerGroupIDArg(parser, required=False)
    flags.AddKafkaSourceInitialOffsetArg(parser, required=False)
    flags.AddKafkaSourceNetworkAttachmentArg(parser, required=True)
    flags.AddKafkaSourceAuthGroup(parser, required=True)
    flags.AddLoggingConfigArg(parser, 'The logging config of the kafka source.')
    labels_util.AddCreateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the create command."""
    client = kafka_sources.KafkaSourceClientV1()
    kafka_source_ref = args.CONCEPTS.kafka_source.Parse()

    log.debug(
        'Creating kafka source {} for project {} in location {}'.format(
            kafka_source_ref.kafkaSourcesId,
            kafka_source_ref.projectsId,
            kafka_source_ref.locationsId,
        )
    )
    operation = client.Create(
        kafka_source_ref,
        client.BuildKafkaSource(
            kafka_source_ref=kafka_source_ref,
            bootstrap_servers=args.bootstrap_servers,
            consumer_group_id=args.consumer_group_id,
            topics=args.topics,
            sasl_mechanism=args.sasl_mechanism,
            sasl_username=args.sasl_username,
            sasl_password=args.sasl_password,
            tls_client_certificate=args.tls_client_certificate,
            tls_client_key=args.tls_client_key,
            network_attachment=args.network_attachment,
            message_bus=args.message_bus,
            initial_offset=args.initial_offset,
            logging_config=args.logging_config,
            labels=labels_util.ParseCreateArgs(args, client.LabelsValueClass()),
        ),
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Creating', kafka_source_ref)
