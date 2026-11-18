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
"""Command to update the specified pipeline."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import pipelines
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To update the pipeline `my-pipeline` with its destination targeting HTTP endpoint URI 'https://example-endpoint.com' and network attachment 'my-network-attachment', run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',network_attachment=my-network-attachment
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update an Eventarc pipeline."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddUpdatePipelineResourceArgs(parser)
    flags.AddPipelineDestinationsArg(parser, required=False)
    flags.AddInputPayloadFormatArgs(parser)
    flags.AddMediationsArg(parser)
    flags.AddLoggingConfigArg(parser, 'The logging config of the pipeline.')
    flags.AddRetryPolicyArgs(parser)
    flags.AddCryptoKeyArg(parser, with_clear=True, hidden=False)
    labels_util.AddUpdateLabelsFlags(parser)

    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the update command."""
    client = pipelines.PipelineClientV1()
    pipeline_ref = args.CONCEPTS.pipeline.Parse()
    error_message_bus_ref = args.CONCEPTS.error_message_bus.Parse()

    log.debug(
        'Updating pipeline {} for project {} in location {}'.format(
            pipeline_ref.pipelinesId,
            pipeline_ref.projectsId,
            pipeline_ref.locationsId,
        )
    )

    original_pipeline = client.Get(pipeline_ref)
    labels_update_result = labels_util.Diff.FromUpdateArgs(args).Apply(
        client.LabelsValueClass(), original_pipeline.labels
    )

    update_mask = client.BuildUpdateMask(
        destinations=args.IsSpecified('destinations'),
        input_payload_format_json=args.IsSpecified('input_payload_format_json'),
        input_payload_format_avro_schema_definition=args.IsSpecified(
            'input_payload_format_avro_schema_definition'
        ),
        input_payload_format_protobuf_schema_definition=args.IsSpecified(
            'input_payload_format_protobuf_schema_definition'
        ),
        mediations=args.IsSpecified('mediations'),
        logging_config=args.IsSpecified('logging_config'),
        max_retry_attempts=args.IsSpecified('max_retry_attempts'),
        min_retry_delay=args.IsSpecified('min_retry_delay'),
        max_retry_delay=args.IsSpecified('max_retry_delay'),
        crypto_key=args.IsSpecified('crypto_key'),
        clear_crypto_key=args.clear_crypto_key,
        labels=labels_update_result.needs_update,
        error_message_bus=args.IsSpecified('error_message_bus'),
        clear_error_message_bus=args.clear_error_message_bus,
    )

    operation = client.Patch(
        pipeline_ref,
        client.BuildPipeline(
            pipeline_ref=pipeline_ref,
            destinations=args.destinations,
            input_payload_format_json=args.input_payload_format_json,
            input_payload_format_avro_schema_definition=args.input_payload_format_avro_schema_definition,
            input_payload_format_protobuf_schema_definition=args.input_payload_format_protobuf_schema_definition,
            mediations=args.mediations,
            logging_config=args.logging_config,
            max_retry_attempts=args.max_retry_attempts,
            min_retry_delay=args.min_retry_delay,
            max_retry_delay=args.max_retry_delay,
            crypto_key_name=args.crypto_key,
            labels=labels_update_result.GetOrNone(),
            error_message_bus_ref=error_message_bus_ref,
        ),
        update_mask,
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Updating', pipeline_ref)
