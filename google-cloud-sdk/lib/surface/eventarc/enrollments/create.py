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
"""Command to create an enrollment."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.eventarc import enrollments
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.eventarc import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

_DETAILED_HELP = {
    'DESCRIPTION': '{description}',
    'EXAMPLES': """ \
        To create a new enrollment `my-enrollment` in location `us-central1` for message-bus `my-message-bus` with cel matching expression `message.type == "google.cloud.pubsub.topic.v1.messagePublished"` and destination pipeline `my-pipeline`, run:

          $ {command} my-enrollment --location=us-central1 --message-bus=my-message-bus --cel-match="message.type == 'google.cloud.pubsub.topic.v1.messagePublished'" --destination-pipeline=my-pipeline
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Create(base.CreateCommand):
  """Create an Eventarc enrollment."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddCreateEnrollmentResourceArgs(parser)
    flags.AddCelMatchArg(parser, required=True)
    labels_util.AddCreateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the create command."""
    client = enrollments.EnrollmentClientV1()
    enrollment_ref = args.CONCEPTS.enrollment.Parse()

    log.debug(
        'Creating enrollment {} for project {} in location {}'.format(
            enrollment_ref.enrollmentsId,
            enrollment_ref.projectsId,
            enrollment_ref.locationsId,
        )
    )
    operation = client.Create(
        enrollment_ref,
        client.BuildEnrollment(
            enrollment_ref,
            args.cel_match,
            args.CONCEPTS.message_bus.Parse(),
            args.CONCEPTS.destination_pipeline.Parse(),
            labels_util.ParseCreateArgs(args, client.LabelsValueClass()),
        ),
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Creating', enrollment_ref)
