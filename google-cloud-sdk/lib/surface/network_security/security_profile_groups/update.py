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
"""Update command to update a security profile group resource."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_security.security_profile_groups import spg_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_security import spg_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log

_detailed_help = {
    'DESCRIPTION': """

          Update details of a Security Profile Group.

        """,
    'EXAMPLES': """
          To update a Security Profile Group with new threat prevention profile `my-new-security-profile`, run:

              $ {command} my-security-profile-group --organization=1234 --location=global --threat-prevention-profile=`organizations/1234/locations/global/securityProfiles/my-new-security-profile` --description='New Security Profile of type threat prevention'

        """,
}

_URL_FILTERING_SUPPORTED = (
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA
)


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class UpdateProfileGroup(base.UpdateCommand):
  """Update a Security Profile Group."""

  @classmethod
  def Args(cls, parser):
    spg_flags.AddSecurityProfileGroupResource(parser, cls.ReleaseTrack())
    spg_flags.AddProfileGroupDescription(parser)
    # TODO: b/349671332 - Remove this conditional once the group is released.
    threat_prevention_group = None
    if cls.ReleaseTrack() in _URL_FILTERING_SUPPORTED:
      threat_prevention_group = parser.add_group(mutex=True)
      threat_prevention_group.add_argument(
          '--clear-threat-prevention-profile',
          action='store_true',
          help='''\
            Clear the threat-prevention-profile field.
          ''',
      )
    spg_flags.AddSecurityProfileResource(
        parser,
        cls.ReleaseTrack(),
        'threat-prevention-profile',
        group=threat_prevention_group,
        required=False,
        arg_aliases=['security-profile'],
    )
    # TODO: b/349671332 - Remove this conditional once the group is released.
    if cls.ReleaseTrack() in _URL_FILTERING_SUPPORTED:
      url_filtering_group = parser.add_group(mutex=True)
      url_filtering_group.add_argument(
          '--clear-url-filtering-profile',
          action='store_true',
          help='''\
            Clear the url-filtering-profile field.
          ''',
      )
      spg_flags.AddSecurityProfileResource(
          parser,
          cls.ReleaseTrack(),
          'url-filtering-profile',
          group=url_filtering_group,
          required=False
      )
    labels_util.AddUpdateLabelsFlags(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    base.ASYNC_FLAG.SetDefault(parser, False)

  def getLabel(self, client, security_profile_group):
    return client.GetSecurityProfileGroup(
        security_profile_group.RelativeName()
    ).labels

  def Run(self, args):
    client = spg_api.Client(self.ReleaseTrack())
    security_profile_group = args.CONCEPTS.security_profile_group.Parse()
    threat_prevention_profile = (
        args.CONCEPTS.threat_prevention_profile.Parse()
        if args.threat_prevention_profile
        else None
    )
    if (
        self.ReleaseTrack() in _URL_FILTERING_SUPPORTED
        and args.url_filtering_profile
    ):
      url_filtering_profile = args.CONCEPTS.url_filtering_profile.Parse()
    else:
      url_filtering_profile = None
    description = args.description
    is_async = args.async_

    labels_update = labels_util.ProcessUpdateArgsLazy(
        args,
        client.messages.SecurityProfileGroup.LabelsValue,
        orig_labels_thunk=lambda: self.getLabel(client, security_profile_group),
    )

    if args.location != 'global':
      raise core_exceptions.Error(
          'Only `global` location is supported, but got: %s' % args.location
      )

    update_mask = []
    if (threat_prevention_profile is not None
        or self.ReleaseTrack() in _URL_FILTERING_SUPPORTED
        and args.clear_threat_prevention_profile):
      update_mask.append('threatPreventionProfile')
    if (url_filtering_profile is not None
        or self.ReleaseTrack() in _URL_FILTERING_SUPPORTED
        and args.clear_url_filtering_profile):
      update_mask.append('urlFilteringProfile')

    if description is not None:
      update_mask.append('description')

    if not update_mask:
      raise core_exceptions.Error(
          'Operation failed to satisfy minimum qualification. Please specify'
          ' the attribute which needs an update. `description` and/or `security'
          ' profile` can be updated.'
      )

    response = client.UpdateSecurityProfileGroup(
        security_profile_group_name=security_profile_group.RelativeName(),
        description=description if description is not None else None,
        threat_prevention_profile=threat_prevention_profile.RelativeName()
        if threat_prevention_profile is not None
        else None,
        url_filtering_profile=url_filtering_profile.RelativeName()
        if url_filtering_profile is not None
        else None,
        update_mask=','.join(update_mask),
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
        message='Waiting for security-profile-group [{}] to be updated'.format(
            security_profile_group.RelativeName()
        ),
        has_result=True,
    )


UpdateProfileGroup.detailed_help = _detailed_help
