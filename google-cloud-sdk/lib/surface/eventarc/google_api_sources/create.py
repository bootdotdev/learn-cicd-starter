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
"""Command to create a Google API source."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import google_api_sources
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To create a new Google API source `my-google-api-source` in location `us-central1` with a destination message bus `my-message-bus`, run:

          $ {command} my-google-api-source --location=us-central1 --destination-message-bus=my-message-bus
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an Eventarc Google API source."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddCreateGoogleApiSourceResourceArgs(parser)
    flags.AddLoggingConfigArg(
        parser, 'The logging config for the Google API source.'
    )
    flags.AddWideScopeSubscriptionArg(parser, with_clear=False)
    flags.AddCryptoKeyArg(parser, with_clear=False, hidden=False)
    labels_util.AddCreateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the create command."""
    client = google_api_sources.GoogleApiSourceClientV1()
    google_api_source_ref = args.CONCEPTS.google_api_source.Parse()

    log.debug(
        'Creating Google API source {} for project {} in location {}'.format(
            google_api_source_ref.googleApiSourcesId,
            google_api_source_ref.projectsId,
            google_api_source_ref.locationsId,
        )
    )
    operation = client.Create(
        google_api_source_ref,
        client.BuildGoogleApiSource(
            google_api_source_ref,
            args.CONCEPTS.destination_message_bus.Parse(),
            args.logging_config,
            args.crypto_key,
            labels_util.ParseCreateArgs(args, client.LabelsValueClass()),
            args.organization_subscription
            if args.IsSpecified('organization_subscription')
            else None,
            args.project_subscriptions,
        ),
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Creating', google_api_source_ref)
