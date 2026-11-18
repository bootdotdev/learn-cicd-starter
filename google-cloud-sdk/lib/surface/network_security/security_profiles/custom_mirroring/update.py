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
"""Update command to update a new Custom Mirroring profile."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.security_profiles import mirroring_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import sp_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

DETAILED_HELP = {
    'DESCRIPTION': """

          Update a Custom Mirroring Security Profile.

          The supported fields for update are `description` and `labels`.

        """,
    'EXAMPLES': """
          To update the description of a Custom Mirroring Security Profile named `mirroring-profile`, run:

              $ {command} mirroring-profile --description="A new description" \
              --organization=1234567890 --location=global

          To change the labels of a Custom Mirroring Security Profile named `mirroring-profile`, run:

              $ {command} mirroring-profile
              --update-labels=key1=value1,key2=value2  \
              --delete-labels=key3,key4 \
              --organization=1234567890 --location=glob
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Updates a Custom Mirroring Profile."""

  detailed_help = DETAILED_HELP

  @classmethod
  def Args(cls, parser):
    sp_flags.AddSecurityProfileResource(parser, cls.ReleaseTrack())
    sp_flags.AddProfileDescription(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)
    labels_util.AddUpdateLabelsFlags(parser)

  def Run(self, args):
    client = mirroring_api.Client(self.ReleaseTrack())
    security_profile = args.CONCEPTS.security_profile.Parse()
    description = args.description
    is_async = args.async_

    labels_update = labels_util.ProcessUpdateArgsLazy(
        args,
        client.messages.SecurityProfile.LabelsValue,
        orig_labels_thunk=lambda: self.getLabels(client, security_profile),
    )

    response = client.UpdateSecurityProfile(
        name=security_profile.RelativeName(),
        description=description,
        labels=labels_update.GetOrNone(),
    )

    # Return the in-progress operation if async is requested.
    if is_async:
      operation_id = response.name
      log.status.Print(
          'Check for operation completion status using operation ID:',
          operation_id,
      )
      return response

    # Default operation poller if async is not specified.
    return client.WaitForOperation(
        operation_ref=client.GetOperationsRef(response),
        message='Waiting for security-profile [{}] to be updated'.format(
            security_profile.RelativeName()
        ),
        has_result=True,
    )

  def getLabels(self, client, security_profile):
    return client.GetSecurityProfile(security_profile.RelativeName()).labels
