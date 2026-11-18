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
"""Command to create a pipeline."""

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
        To create a new pipeline `my-pipeline` in location `us-central1` with its destination targeting HTTP endpoint URI 'https://example-endpoint.com', run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination and a message binding template, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',http_endpoint_message_binding_template='{"headers": {"new-header-key": "new-header-value"}}'

        To create a new pipeline `my-pipeline` in location `us-central1` with a Cloud Workflow destination `my-workflow`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=workflow=my-workflow

        To create a new pipeline `my-pipeline` in location `us-central1` with a message bus destination `my-message-bus`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=message_bus=my-message-bus

        To create a new pipeline `my-pipeline` in location `us-central1` with a Cloud Pub/Sub Topic destination `my-topic`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=pubsub_topic=my-topic

        To create a new pipeline `my-pipeline` in location `us-central1` with a Cloud Workflow in project `example-project` and location `us-east1`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=workflow=my-workflow,project=example-project,location=us-east1

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a service account `example-service-account@example-project.gserviceaccount.iam.com` for OIDC authentication, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',google_oidc_authentication_service_account=example-service-account@example-project.gserviceaccount.iam.com

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a service account `example-service-account@example-project.gserviceaccount.iam.com` for OIDC authentication with audience `https://example.com`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',google_oidc_authentication_service_account=example-service-account@example-project.gserviceaccount.iam.com,google_oidc_authentication_audience='https://example.com'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a service account `example-service-account@example-project.gserviceaccount.iam.com` for OAuth token authentication, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',oauth_token_authentication_service_account=example-service-account@example-project.gserviceaccount.iam.com

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a service account `example-service-account@example-project.gserviceaccount.iam.com` for OAuth token authentication with scope `https://www.googleapis.com/auth/cloud-platform`, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',oauth_token_authentication_service_account=example-service-account@example-project.gserviceaccount.iam.com,oauth_token_authentication_scope='https://www.googleapis.com/auth/cloud-platform'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and the JSON input and output payload formats, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',output_payload_format_json= --input-payload-format-json=

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and the Avro input and output payload formats, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',output_payload_format_avro_schema_definition='{"type": "record", "name": "my_record", "fields": [{"name": "my_field", "type": "string"}]}' --input-payload-format-avro-schema-definition='{"type": "record", "name": "my_record", "fields": [{"name": "my_field", "type": "string"}]}'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and the Protobuf input and output payload formats, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com',output_payload_format_protobuf_schema_definition='syntax = "proto3"; message Location { string home_address = 1; }' --input-payload-format-protobuf-schema-definition='syntax = "proto3"; message Location { string home_address = 1; }'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a transformation mediation, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com'--mediations=transformation_template='message.removeFields(["data.credit_card_number","data.ssn"])'

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a INFO level logging configuration, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com'--logging_config=INFO

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a custom retry policy, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com' --max-retry-attempts=10 --min-retry-delay=2s --max-retry-delay=64s

        To create a new pipeline `my-pipeline` in location `us-central1` with an HTTP endpoint URI destination `https://example-endpoint.com` and a Cloud KMS CryptoKey, run:

          $ {command} my-pipeline --location=us-central1 --destinations=http_endpoint_uri='https://example-endpoint.com'  --crypto-key=projects/PROJECT_ID/locations/KMS_LOCATION/keyRings/KEYRING/cryptoKeys/KEY
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an Eventarc pipeline."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddCreatePipelineResourceArgs(parser)
    flags.AddPipelineDestinationsArg(parser, required=True)
    flags.AddInputPayloadFormatArgs(parser)
    flags.AddMediationsArg(parser)
    flags.AddLoggingConfigArg(parser, 'The logging config of the pipeline.')
    flags.AddRetryPolicyArgs(parser)
    flags.AddCryptoKeyArg(parser, with_clear=False, hidden=False)
    labels_util.AddCreateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the create command."""
    client = pipelines.PipelineClientV1()
    pipelines_ref = args.CONCEPTS.pipeline.Parse()
    error_message_bus_ref = args.CONCEPTS.error_message_bus.Parse()

    log.debug(
        'Creating pipeline {} for project {} in location {}'.format(
            pipelines_ref.pipelinesId,
            pipelines_ref.projectsId,
            pipelines_ref.locationsId,
        )
    )
    operation = client.Create(
        pipelines_ref,
        client.BuildPipeline(
            pipeline_ref=pipelines_ref,
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
            labels=labels_util.ParseCreateArgs(args, client.LabelsValueClass()),
            error_message_bus_ref=error_message_bus_ref,
        ),
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Creating', pipelines_ref)
