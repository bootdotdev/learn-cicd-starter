# -*- coding: utf-8 -*- #
# Copyright 2017 Google LLC. All Rights Reserved.
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
"""Cloud Pub/Sub topic describe command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.pubsub import topics
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.pubsub import resource_args


def _FormatRequiresDelimiterEscaping(output_format):
  return (
      output_format is None
      or output_format.startswith('yaml')
      or output_format.startswith('default')
  )


@base.UniverseCompatible
class Describe(base.DescribeCommand):
  """Describes a Cloud Pub/Sub topic."""

  @staticmethod
  def Args(parser):
    resource_args.AddTopicResourceArg(parser, 'to describe.')

  def Run(self, args):
    client = topics.TopicsClient()
    topic_ref = args.CONCEPTS.topic.Parse()
    topic_result = client.Get(topic_ref)
    if (not _FormatRequiresDelimiterEscaping(args.format)):
      return topic_result

    # Ensure that the newline character is displayed correctly when used as the
    # delimiter for ingestion from Cloud Storage.
    ingestion_settings = topic_result.ingestionDataSourceSettings
    if (
        ingestion_settings
        and ingestion_settings.cloudStorage
        and ingestion_settings.cloudStorage.textFormat
        and ingestion_settings.cloudStorage.textFormat.delimiter == '\n'
    ):
      topic_result.ingestionDataSourceSettings.cloudStorage.textFormat.delimiter = (
          '\\n'
      )

    return topic_result
