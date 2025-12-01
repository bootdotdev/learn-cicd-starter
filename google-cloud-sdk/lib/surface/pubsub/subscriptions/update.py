# -*- coding: utf-8 -*- #
# Copyright 2016 Google LLC. All Rights Reserved.
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
"""Cloud Pub/Sub subscriptions update command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.pubsub import subscriptions
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.pubsub import flags
from googlecloudsdk.command_lib.pubsub import resource_args
from googlecloudsdk.command_lib.pubsub import util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


def _Args(
    parser,
    enable_push_to_cps=False,
):
  """Adds the arguments for this command.

  Args:
    parser: the parser for the command.
    enable_push_to_cps: whether or not to enable Pubsub Export config flags
      support.
  """
  resource_args.AddSubscriptionResourceArg(parser, 'to update.')
  flags.AddSubscriptionSettingsFlags(
      parser,
      is_update=True,
      enable_push_to_cps=enable_push_to_cps,
  )
  labels_util.AddUpdateLabelsFlags(parser)
  flags.AddMessageTransformsFlags(parser, is_update=True)


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Updates an existing Cloud Pub/Sub subscription."""

  @classmethod
  def Args(cls, parser):
    _Args(parser)

  @exceptions.CatchHTTPErrorRaiseHTTPException()
  def Run(
      self,
      args,
      enable_push_to_cps=False,
  ):
    """This is what gets called when the user runs this command.

    Args:
      args: An argparse namespace. All the arguments that were provided to this
        command invocation.
      enable_push_to_cps: Whether or not to enable Pubsub Export config flags
        support.

    Returns:
      A serialized object (dict) describing the results of the operation. This
      description fits the Resource described in the ResourceRegistry under
      'pubsub.projects.subscriptions'.

    Raises:
      An HttpException if there was a problem calling the
      API subscriptions.Patch command.
    """
    flags.ValidateDeadLetterPolicy(args)

    client = subscriptions.SubscriptionsClient()
    subscription_ref = args.CONCEPTS.subscription.Parse()
    dead_letter_topic = getattr(args, 'dead_letter_topic', None)
    max_delivery_attempts = getattr(args, 'max_delivery_attempts', None)
    clear_dead_letter_policy = getattr(args, 'clear_dead_letter_policy', None)
    clear_retry_policy = getattr(args, 'clear_retry_policy', None)
    clear_bigquery_config = getattr(args, 'clear_bigquery_config', None)
    clear_cloud_storage_config = getattr(
        args, 'clear_cloud_storage_config', None
    )
    clear_push_no_wrapper_config = getattr(
        args, 'clear_push_no_wrapper_config', None
    )
    clear_pubsub_export_config = (
        getattr(args, 'clear_pubsub_export_config', None)
        if enable_push_to_cps
        else None
    )

    labels_update = labels_util.ProcessUpdateArgsLazy(
        args,
        client.messages.Subscription.LabelsValue,
        orig_labels_thunk=lambda: client.Get(subscription_ref).labels,
    )

    no_expiration = False
    expiration_period = getattr(args, 'expiration_period', None)
    if expiration_period:
      if expiration_period == subscriptions.NEVER_EXPIRATION_PERIOD_VALUE:
        no_expiration = True
        expiration_period = None

    if dead_letter_topic:
      dead_letter_topic = args.CONCEPTS.dead_letter_topic.Parse().RelativeName()

    min_retry_delay = getattr(args, 'min_retry_delay', None)
    if args.IsSpecified('min_retry_delay'):
      min_retry_delay = util.FormatDuration(min_retry_delay)
    max_retry_delay = getattr(args, 'max_retry_delay', None)
    if args.IsSpecified('max_retry_delay'):
      max_retry_delay = util.FormatDuration(max_retry_delay)
    bigquery_table = getattr(args, 'bigquery_table', None)
    use_topic_schema = getattr(args, 'use_topic_schema', None)
    use_table_schema = getattr(args, 'use_table_schema', None)
    write_metadata = getattr(args, 'write_metadata', None)
    drop_unknown_fields = getattr(args, 'drop_unknown_fields', None)
    bigquery_service_account_email = getattr(
        args, 'bigquery_service_account_email', None
    )
    cloud_storage_bucket = getattr(args, 'cloud_storage_bucket', None)
    cloud_storage_file_prefix = getattr(args, 'cloud_storage_file_prefix', None)
    cloud_storage_file_suffix = getattr(args, 'cloud_storage_file_suffix', None)
    cloud_storage_file_datetime_format = getattr(
        args, 'cloud_storage_file_datetime_format', None
    )
    cloud_storage_max_bytes = getattr(args, 'cloud_storage_max_bytes', None)
    cloud_storage_max_duration = getattr(
        args, 'cloud_storage_max_duration', None
    )
    cloud_storage_max_messages = getattr(
        args, 'cloud_storage_max_messages', None
    )
    if args.IsSpecified('cloud_storage_max_duration'):
      cloud_storage_max_duration = util.FormatDuration(
          cloud_storage_max_duration
      )
    cloud_storage_output_format_list = getattr(
        args, 'cloud_storage_output_format', None
    )
    cloud_storage_output_format = None
    if cloud_storage_output_format_list:
      cloud_storage_output_format = cloud_storage_output_format_list[0]
    cloud_storage_use_topic_schema = getattr(
        args, 'cloud_storage_use_topic_schema', None
    )
    cloud_storage_write_metadata = getattr(
        args, 'cloud_storage_write_metadata', None
    )
    cloud_storage_service_account_email = getattr(
        args, 'cloud_storage_service_account_email', None
    )
    pubsub_export_topic = (
        getattr(args, 'pubsub_export_topic', None)
        if enable_push_to_cps
        else None
    )

    if pubsub_export_topic:
      pubsub_export_topic = (
          args.CONCEPTS.pubsub_export_topic.Parse().RelativeName()
      )

    pubsub_export_topic_region = getattr(
        args, 'pubsub_export_topic_region', None
    )

    enable_exactly_once_delivery = getattr(
        args, 'enable_exactly_once_delivery', None
    )

    message_transforms_file = getattr(args, 'message_transforms_file', None)
    clear_message_transforms = getattr(args, 'clear_message_transforms', None)

    try:
      result = client.Patch(
          subscription_ref,
          ack_deadline=args.ack_deadline,
          push_config=util.ParsePushConfig(args),
          retain_acked_messages=args.retain_acked_messages,
          labels=labels_update.GetOrNone(),
          message_retention_duration=args.message_retention_duration,
          no_expiration=no_expiration,
          expiration_period=expiration_period,
          dead_letter_topic=dead_letter_topic,
          max_delivery_attempts=max_delivery_attempts,
          clear_dead_letter_policy=clear_dead_letter_policy,
          clear_retry_policy=clear_retry_policy,
          min_retry_delay=min_retry_delay,
          max_retry_delay=max_retry_delay,
          enable_exactly_once_delivery=enable_exactly_once_delivery,
          bigquery_table=bigquery_table,
          use_topic_schema=use_topic_schema,
          use_table_schema=use_table_schema,
          write_metadata=write_metadata,
          drop_unknown_fields=drop_unknown_fields,
          bigquery_service_account_email=bigquery_service_account_email,
          clear_bigquery_config=clear_bigquery_config,
          cloud_storage_bucket=cloud_storage_bucket,
          cloud_storage_file_prefix=cloud_storage_file_prefix,
          cloud_storage_file_suffix=cloud_storage_file_suffix,
          cloud_storage_file_datetime_format=cloud_storage_file_datetime_format,
          cloud_storage_max_bytes=cloud_storage_max_bytes,
          cloud_storage_max_duration=cloud_storage_max_duration,
          cloud_storage_max_messages=cloud_storage_max_messages,
          cloud_storage_output_format=cloud_storage_output_format,
          cloud_storage_use_topic_schema=cloud_storage_use_topic_schema,
          cloud_storage_write_metadata=cloud_storage_write_metadata,
          cloud_storage_service_account_email=cloud_storage_service_account_email,
          clear_cloud_storage_config=clear_cloud_storage_config,
          clear_push_no_wrapper_config=clear_push_no_wrapper_config,
          pubsub_export_topic=pubsub_export_topic,
          pubsub_export_topic_region=pubsub_export_topic_region,
          clear_pubsub_export_config=clear_pubsub_export_config,
          message_transforms_file=message_transforms_file,
          clear_message_transforms=clear_message_transforms,
      )
    except subscriptions.NoFieldsSpecifiedError:
      if not any(
          args.IsSpecified(arg)
          for arg in ('clear_labels', 'update_labels', 'remove_labels')
      ):
        raise
      log.status.Print('No update to perform.')
      result = None
    else:
      log.UpdatedResource(subscription_ref.RelativeName(), kind='subscription')
    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Updates an existing Cloud Pub/Sub subscription."""

  @classmethod
  def Args(cls, parser):
    _Args(
        parser,
        enable_push_to_cps=True,
    )

  @exceptions.CatchHTTPErrorRaiseHTTPException()
  def Run(self, args):
    return super(UpdateBeta, self).Run(args, enable_push_to_cps=True)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateBeta):
  """Updates an existing Cloud Pub/Sub subscription."""

  @classmethod
  def Args(cls, parser):
    super(UpdateAlpha, cls).Args(parser)
