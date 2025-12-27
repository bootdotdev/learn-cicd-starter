# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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
"""Cloud Pub/Sub topics create command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as api_ex
from googlecloudsdk.api_lib.pubsub import topics
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.kms import resource_args as kms_resource_args
from googlecloudsdk.command_lib.pubsub import flags
from googlecloudsdk.command_lib.pubsub import resource_args
from googlecloudsdk.command_lib.pubsub import util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core import properties

_KMS_FLAG_OVERRIDES = {
    'kms-key': '--topic-encryption-key',
    'kms-keyring': '--topic-encryption-key-keyring',
    'kms-location': '--topic-encryption-key-location',
    'kms-project': '--topic-encryption-key-project',
}

_KMS_PERMISSION_INFO = """
The specified Cloud KMS key should have purpose set to "ENCRYPT_DECRYPT".
The service account,
"service-${CONSUMER_PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com"
requires the IAM cryptoKeyEncrypterDecrypter role for the given Cloud KMS key.
CONSUMER_PROJECT_NUMBER is the project number of the project that is the parent of the
topic being created"""


def _GetKmsKeyPresentationSpec():
  return kms_resource_args.GetKmsKeyPresentationSpec(
      'topic',
      flag_overrides=_KMS_FLAG_OVERRIDES,
      permission_info=_KMS_PERMISSION_INFO,
  )


def _GetTopicPresentationSpec():
  return resource_args.CreateTopicResourceArg(
      'to create.', positional=True, plural=True
  )


def _Run(args, legacy_output=False):
  """Creates one or more topics."""
  client = topics.TopicsClient()

  labels = labels_util.ParseCreateArgs(args, client.messages.Topic.LabelsValue)

  kms_key = None
  kms_ref = args.CONCEPTS.kms_key.Parse()
  if kms_ref:
    kms_key = kms_ref.RelativeName()
  else:
    # Did user supply any topic-encryption-key flags?
    for keyword in [
        'topic-encryption-key',
        'topic-encryption-key-project',
        'topic-encryption-key-location',
        'topic-encryption-key-keyring',
    ]:
      if args.IsSpecified(keyword.replace('-', '_')):
        raise core_exceptions.Error(
            '--topic-encryption-key was not fully specified.'
        )

  retention_duration = getattr(args, 'message_retention_duration', None)
  if args.IsSpecified('message_retention_duration'):
    retention_duration = util.FormatDuration(retention_duration)

  message_storage_policy_allowed_regions = (
      args.message_storage_policy_allowed_regions
  )

  message_storage_policy_enforce_in_transit = getattr(
      args, 'message_storage_policy_enforce_in_transit', None
  )

  schema = getattr(args, 'schema', None)
  first_revision_id = None
  last_revision_id = None
  if schema:
    schema = args.CONCEPTS.schema.Parse().RelativeName()
    first_revision_id = getattr(args, 'first_revision_id', None)
    last_revision_id = getattr(args, 'last_revision_id', None)
  message_encoding_list = getattr(args, 'message_encoding', None)
  message_encoding = None
  if message_encoding_list:
    message_encoding = message_encoding_list[0]

  kinesis_ingestion_stream_arn = getattr(
      args, 'kinesis_ingestion_stream_arn', None
  )
  kinesis_ingestion_consumer_arn = getattr(
      args, 'kinesis_ingestion_consumer_arn', None
  )
  kinesis_ingestion_role_arn = getattr(args, 'kinesis_ingestion_role_arn', None)
  kinesis_ingestion_service_account = getattr(
      args, 'kinesis_ingestion_service_account', None
  )

  cloud_storage_ingestion_bucket = getattr(
      args, 'cloud_storage_ingestion_bucket', None
  )
  cloud_storage_ingestion_input_format_list = getattr(
      args, 'cloud_storage_ingestion_input_format', None
  )
  cloud_storage_ingestion_input_format = None
  if cloud_storage_ingestion_input_format_list:
    cloud_storage_ingestion_input_format = (
        cloud_storage_ingestion_input_format_list[0]
    )
  cloud_storage_ingestion_text_delimiter = getattr(
      args, 'cloud_storage_ingestion_text_delimiter', None
  )
  if cloud_storage_ingestion_text_delimiter:
    # Interprets special characters representations (i.e., "\n") as their
    # expected characters (i.e., newline).
    cloud_storage_ingestion_text_delimiter = (
        cloud_storage_ingestion_text_delimiter.encode('utf-8').decode(
            'unicode-escape'
        )
    )
  cloud_storage_ingestion_minimum_object_create_time = getattr(
      args, 'cloud_storage_ingestion_minimum_object_create_time', None
  )
  cloud_storage_ingestion_match_glob = getattr(
      args, 'cloud_storage_ingestion_match_glob', None
  )

  azure_event_hubs_ingestion_resource_group = getattr(
      args, 'azure_event_hubs_ingestion_resource_group', None
  )
  azure_event_hubs_ingestion_namespace = getattr(
      args, 'azure_event_hubs_ingestion_namespace', None
  )
  azure_event_hubs_ingestion_event_hub = getattr(
      args, 'azure_event_hubs_ingestion_event_hub', None
  )
  azure_event_hubs_ingestion_client_id = getattr(
      args, 'azure_event_hubs_ingestion_client_id', None
  )
  azure_event_hubs_ingestion_tenant_id = getattr(
      args, 'azure_event_hubs_ingestion_tenant_id', None
  )
  azure_event_hubs_ingestion_subscription_id = getattr(
      args, 'azure_event_hubs_ingestion_subscription_id', None
  )
  azure_event_hubs_ingestion_service_account = getattr(
      args, 'azure_event_hubs_ingestion_service_account', None
  )
  aws_msk_ingestion_cluster_arn = getattr(
      args, 'aws_msk_ingestion_cluster_arn', None
  )
  aws_msk_ingestion_topic = getattr(args, 'aws_msk_ingestion_topic', None)
  aws_msk_ingestion_aws_role_arn = getattr(
      args, 'aws_msk_ingestion_aws_role_arn', None
  )
  aws_msk_ingestion_service_account = getattr(
      args, 'aws_msk_ingestion_service_account', None
  )
  confluent_cloud_ingestion_bootstrap_server = getattr(
      args, 'confluent_cloud_ingestion_bootstrap_server', None
  )
  confluent_cloud_ingestion_cluster_id = getattr(
      args, 'confluent_cloud_ingestion_cluster_id', None
  )
  confluent_cloud_ingestion_topic = getattr(
      args, 'confluent_cloud_ingestion_topic', None
  )
  confluent_cloud_ingestion_identity_pool_id = getattr(
      args, 'confluent_cloud_ingestion_identity_pool_id', None
  )
  confluent_cloud_ingestion_service_account = getattr(
      args, 'confluent_cloud_ingestion_service_account', None
  )
  ingestion_log_severity = getattr(args, 'ingestion_log_severity', None)
  message_transforms_file = getattr(args, 'message_transforms_file', None)

  tags = flags.GetTagsMessage(args, client.messages.Topic.TagsValue)

  failed = []
  for topic_ref in args.CONCEPTS.topic.Parse():
    try:
      result = client.Create(
          topic_ref,
          labels=labels,
          kms_key=kms_key,
          message_retention_duration=retention_duration,
          message_storage_policy_allowed_regions=message_storage_policy_allowed_regions,
          message_storage_policy_enforce_in_transit=message_storage_policy_enforce_in_transit,
          schema=schema,
          message_encoding=message_encoding,
          first_revision_id=first_revision_id,
          last_revision_id=last_revision_id,
          kinesis_ingestion_stream_arn=kinesis_ingestion_stream_arn,
          kinesis_ingestion_consumer_arn=kinesis_ingestion_consumer_arn,
          kinesis_ingestion_role_arn=kinesis_ingestion_role_arn,
          kinesis_ingestion_service_account=kinesis_ingestion_service_account,
          cloud_storage_ingestion_bucket=cloud_storage_ingestion_bucket,
          cloud_storage_ingestion_input_format=cloud_storage_ingestion_input_format,
          cloud_storage_ingestion_text_delimiter=cloud_storage_ingestion_text_delimiter,
          cloud_storage_ingestion_minimum_object_create_time=cloud_storage_ingestion_minimum_object_create_time,
          cloud_storage_ingestion_match_glob=cloud_storage_ingestion_match_glob,
          azure_event_hubs_ingestion_resource_group=azure_event_hubs_ingestion_resource_group,
          azure_event_hubs_ingestion_namespace=azure_event_hubs_ingestion_namespace,
          azure_event_hubs_ingestion_event_hub=azure_event_hubs_ingestion_event_hub,
          azure_event_hubs_ingestion_client_id=azure_event_hubs_ingestion_client_id,
          azure_event_hubs_ingestion_tenant_id=azure_event_hubs_ingestion_tenant_id,
          azure_event_hubs_ingestion_subscription_id=azure_event_hubs_ingestion_subscription_id,
          azure_event_hubs_ingestion_service_account=azure_event_hubs_ingestion_service_account,
          aws_msk_ingestion_cluster_arn=aws_msk_ingestion_cluster_arn,
          aws_msk_ingestion_topic=aws_msk_ingestion_topic,
          aws_msk_ingestion_aws_role_arn=aws_msk_ingestion_aws_role_arn,
          aws_msk_ingestion_service_account=aws_msk_ingestion_service_account,
          confluent_cloud_ingestion_bootstrap_server=confluent_cloud_ingestion_bootstrap_server,
          confluent_cloud_ingestion_cluster_id=confluent_cloud_ingestion_cluster_id,
          confluent_cloud_ingestion_topic=confluent_cloud_ingestion_topic,
          confluent_cloud_ingestion_identity_pool_id=confluent_cloud_ingestion_identity_pool_id,
          confluent_cloud_ingestion_service_account=confluent_cloud_ingestion_service_account,
          ingestion_log_severity=ingestion_log_severity,
          message_transforms_file=message_transforms_file,
          tags=tags,
      )
    except api_ex.HttpError as error:
      exc = exceptions.HttpException(error)
      log.CreatedResource(
          topic_ref.RelativeName(),
          kind='topic',
          failed=util.CreateFailureErrorMessage(exc.payload.status_message),
      )
      failed.append(topic_ref.topicsId)
      continue

    if legacy_output:
      result = util.TopicDisplayDict(result)
    log.CreatedResource(topic_ref.RelativeName(), kind='topic')
    yield result

  if failed:
    raise util.RequestsFailedError(failed, 'create')


def _Args(
    parser,
):
  """Custom args implementation.

  Args:
    parser: The current parser.
  """

  resource_args.AddResourceArgs(
      parser, [_GetKmsKeyPresentationSpec(), _GetTopicPresentationSpec()]
  )
  # This group should not be hidden
  flags.AddSchemaSettingsFlags(parser, is_update=False)
  flags.AddIngestionDatasourceFlags(
      parser,
      is_update=False,
  )

  labels_util.AddCreateLabelsFlags(parser)
  flags.AddTopicMessageRetentionFlags(parser, is_update=False)

  flags.AddTopicMessageStoragePolicyFlags(parser, is_update=False)
  flags.AddMessageTransformsFlags(parser)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  """Creates one or more Cloud Pub/Sub topics."""

  detailed_help = {'EXAMPLES': """\
          To create a Cloud Pub/Sub topic, run:

              $ {command} mytopic"""}

  @staticmethod
  def Args(parser):
    _Args(
        parser,
    )

  def Run(self, args):
    return _Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Creates one or more Cloud Pub/Sub topics."""

  @staticmethod
  def Args(parser):
    _Args(
        parser,
    )

  def Run(self, args):
    legacy_output = properties.VALUES.pubsub.legacy_output.GetBool()
    return _Run(args, legacy_output=legacy_output)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(CreateBeta):
  """Creates one or more Cloud Pub/Sub topics."""

  @staticmethod
  def Args(parser):
    super(CreateAlpha, CreateAlpha).Args(parser)
    flags.AddTagsFlag(parser)
