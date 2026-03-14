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
"""Command to update the specified enrollment."""

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
        To update the enrollment `my-enrollment` with a new CEL expression `message.type == 'google.cloud.pubsub.topic.v1.messagePublished'`, run:

          $ {command} my-enrollment --location=us-central1 --cel-match="message.type == 'google.cloud.pubsub.topic.v1.messagePublished'"
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.GA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update an Eventarc enrollment."""

  detailed_help = _DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    flags.AddUpdateEnrollmentResourceArgs(parser)
    flags.AddCelMatchArg(parser, required=False)
    labels_util.AddUpdateLabelsFlags(parser)

    base.ASYNC_FLAG.AddToParser(parser)

  def Run(self, args):
    """Run the update command."""
    client = enrollments.EnrollmentClientV1()
    enrollment_ref = args.CONCEPTS.enrollment.Parse()

    log.debug(
        'Updating enrollment {} for project {} in location {}'.format(
            enrollment_ref.enrollmentsId,
            enrollment_ref.projectsId,
            enrollment_ref.locationsId,
        )
    )

    original_enrollment = client.Get(enrollment_ref)
    labels_update_result = labels_util.Diff.FromUpdateArgs(args).Apply(
        client.LabelsValueClass(), original_enrollment.labels
    )

    update_mask = client.BuildUpdateMask(
        cel_match=args.IsSpecified('cel_match'),
        destination=args.IsSpecified('destination_pipeline'),
        labels=labels_update_result.needs_update,
    )

    operation = client.Patch(
        enrollment_ref,
        client.BuildEnrollment(
            enrollment_ref=enrollment_ref,
            cel_match=args.cel_match,
            message_bus_ref=None,
            destination_ref=args.CONCEPTS.destination_pipeline.Parse(),
            labels=labels_update_result.GetOrNone(),
        ),
        update_mask,
    )

    if args.async_:
      return operation
    return client.WaitFor(operation, 'Updating', enrollment_ref)
