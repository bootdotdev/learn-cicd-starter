# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""Command for deleting access approval settings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.access_approval import settings
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.access_approval import parent


_PREFERENCES = ('ORGANIZATION', 'FOLDER', 'PROJECT')
_APPROVAL_POLICY_PREFERENCES = (
    'transparency',
    'streamlined-support',
    'access-approval',
    'inherit-policy-from-parent',
)


@base.UniverseCompatible
class Update(base.Command):
  """Update Access Approval settings.

  Update the Access Approval settings associated with a project, a folder, or
  organization. Partial updates are supported (for example, you can update the
  notification emails without modifying the enrolled services).
  """

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
    Update notification emails associated with project `p1`, run:

        $ {command} --project=p1 --notification_emails='foo@example.com, bar@example.com'

    Enable Access Approval enforcement for folder `f1`:

        $ {command} --folder=f1 --enrolled_services=all

    Enable Access Approval enforcement for organization `org1` for only Cloud Storage and Compute
    products and set the notification emails at the same time:

        $ {command} --organization=org1 --enrolled_services='storage.googleapis.com,compute.googleapis.com' --notification_emails='security_team@example.com'

    Update active key version for project `p1`:

        $ {command} --project=p1 --active_key_version='projects/p1/locations/global/keyRings/signing-keys/cryptoKeys/signing-key/cryptoKeyVersions/1'

    Update preferred request expiration days for project `p1`:

        $ {command} --project=p1 --preferred_request_expiration_days=5

    Enable prefer no broad approval requests for project `p1`:

        $ {command} --project=p1 --prefer_no_broad_approval_requests=true

    Update notification pubsub topic for project `p1`:

        $ {command} --project=p1 --notification_pubsub_topic='exampleTopic'

    Update request scope max width preference for project `p1`:

        $ {command} --project=p1 --request_scope_max_width_preference=PROJECT

    Update approval policy for project `p1`:

        $ {command} --project=p1 --approval_policy=transparency
        """),
  }

  @staticmethod
  def Args(parser):
    """Add command-specific args."""
    parent.Args(parser)
    parser.add_argument(
        '--notification_emails',
        help=(
            'Comma-separated list of email addresses to which notifications'
            " relating to approval requests should be sent or '' to clear all"
            ' saved notification emails.'
        ),
    )
    parser.add_argument(
        '--enrolled_services',
        help=(
            'Comma-separated list of services to enroll for Access Approval or'
            " 'all' for all supported services. Note for project and folder"
            " enrollments, only 'all' is supported. Use '' to clear all"
            ' enrolled services.'
        ),
    )
    parser.add_argument(
        '--active_key_version',
        help=(
            'The asymmetric crypto key version to use for signing approval'
            " requests. Use '' to remove the custom signing key."
        ),
    )
    parser.add_argument(
        '--preferred_request_expiration_days',
        type=int,
        help=(
            'The default expiration time for approval requests. This value must'
            ' be between 1 and 30. Note that this can be overridden at time of'
            ' Approval Request creation and modified by the customer at'
            ' approval time.'
        ),
    )
    parser.add_argument(
        '--prefer_no_broad_approval_requests',
        type=bool,
        help=(
            'If set to true it will communicate the preference to Google'
            ' personnel to request access with as targeted a resource scope as'
            ' possible.'
        ),
    )
    parser.add_argument(
        '--notification_pubsub_topic',
        help=(
            'The pubsub topic to publish notifications to when approval'
            ' requests are made.'
        ),
    )
    parser.add_argument(
        '--request_scope_max_width_preference',
        choices=_PREFERENCES,
        help=(
            'The preference for the broadest scope of access for access'
            ' requests without a specific method.'
        ),
    )
    parser.add_argument(
        '--require_customer_visible_justification',
        type=bool,
        help=(
            'The preference to configure if a customer visible justification'
            ' (i.e. Vector Case) is required for a Googler to create an Access'
            ' Ticket to send to the customer when attempting to access customer'
            ' resources.'
        ),
    )
    parser.add_argument(
        '--approval_policy',
        choices=_APPROVAL_POLICY_PREFERENCES,
        help=(
            'The preference to configure the approval policy for access'
            ' requests.'
        ),
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    p = parent.GetParent(args)

    if (
        args.notification_emails is None
        and args.enrolled_services is None
        and args.active_key_version is None
        and args.preferred_request_expiration_days is None
        and args.prefer_no_broad_approval_requests is None
        and args.notification_pubsub_topic is None
        and args.request_scope_max_width_preference is None
        and args.require_customer_visible_justification is None
        and args.approval_policy is None
    ):
      raise exceptions.MinimumArgumentException(
          [
              '--notification_emails',
              '--enrolled_services',
              '--active_key_version',
              '--preferred_request_expiration_days',
              '--prefer_no_broad_approval_requests',
              '--notification_pubsub_topic',
              '--request_scope_max_width_preference',
              '--require_customer_visible_justification',
              '--approval_policy',
          ],
          'must specify at least one of these flags',
      )

    update_mask = []
    emails_list = []
    if args.notification_emails is not None:
      update_mask.append('notification_emails')
      if args.notification_emails:
        emails_list = args.notification_emails.split(',')
        emails_list = [i.strip() for i in emails_list]

    services_list = []
    if args.enrolled_services is not None:
      update_mask.append('enrolled_services')
      if args.enrolled_services:
        services_list = args.enrolled_services.split(',')
        services_list = [i.strip() for i in services_list]

    if args.active_key_version is not None:
      update_mask.append('active_key_version')

    if args.preferred_request_expiration_days is not None:
      update_mask.append('preferred_request_expiration_days')

    if args.prefer_no_broad_approval_requests is not None:
      update_mask.append('prefer_no_broad_approval_requests')

    if args.notification_pubsub_topic is not None:
      update_mask.append('notification_pubsub_topic')

    msgs = apis.GetMessagesModule('accessapproval', 'v1')
    request_scope_max_width_preference = None
    if args.request_scope_max_width_preference is not None:
      update_mask.append('request_scope_max_width_preference')

      # Converts the string value of the RequestScopeMaxWidthPreference flag
      # passed on the command line into the correct enum value.
      preference_arg = args.request_scope_max_width_preference
      if preference_arg == 'ORGANIZATION':
        request_scope_max_width_preference = (
            msgs.AccessApprovalSettings.RequestScopeMaxWidthPreferenceValueValuesEnum.ORGANIZATION
        )
      elif preference_arg == 'FOLDER':
        request_scope_max_width_preference = (
            msgs.AccessApprovalSettings.RequestScopeMaxWidthPreferenceValueValuesEnum.FOLDER
        )
      elif preference_arg == 'PROJECT':
        request_scope_max_width_preference = (
            msgs.AccessApprovalSettings.RequestScopeMaxWidthPreferenceValueValuesEnum.PROJECT
        )

    if args.require_customer_visible_justification is not None:
      update_mask.append('require_customer_visible_justification')

    if args.approval_policy is not None:
      update_mask.append('approval_policy')

      approval_policy_arg = args.approval_policy
      if approval_policy_arg == 'transparency':
        approval_policy = msgs.CustomerApprovalApprovalPolicy(
            justificationBasedApprovalPolicy=msgs.CustomerApprovalApprovalPolicy.JustificationBasedApprovalPolicyValueValuesEnum.JUSTIFICATION_BASED_APPROVAL_ENABLED_ALL
        )
      elif (
          approval_policy_arg
          == 'streamlined-support'
      ):
        approval_policy = msgs.CustomerApprovalApprovalPolicy(
            justificationBasedApprovalPolicy=msgs.CustomerApprovalApprovalPolicy.JustificationBasedApprovalPolicyValueValuesEnum.JUSTIFICATION_BASED_APPROVAL_ENABLED_EXTERNAL_JUSTIFICATIONS
        )
      elif approval_policy_arg == 'access-approval':
        approval_policy = msgs.CustomerApprovalApprovalPolicy(
            justificationBasedApprovalPolicy=msgs.CustomerApprovalApprovalPolicy.JustificationBasedApprovalPolicyValueValuesEnum.JUSTIFICATION_BASED_APPROVAL_NOT_ENABLED
        )
      elif approval_policy_arg == 'inherit-policy-from-parent':
        approval_policy = msgs.CustomerApprovalApprovalPolicy(
            justificationBasedApprovalPolicy=msgs.CustomerApprovalApprovalPolicy.JustificationBasedApprovalPolicyValueValuesEnum.JUSTIFICATION_BASED_APPROVAL_INHERITED
        )
    else:
      approval_policy = None

    return settings.Update(
        name=f'{p}/accessApprovalSettings',
        notification_emails=emails_list,
        enrolled_services=services_list,
        active_key_version=args.active_key_version,
        preferred_request_expiration_days=args.preferred_request_expiration_days,
        prefer_no_broad_approval_requests=args.prefer_no_broad_approval_requests,
        notification_pubsub_topic=args.notification_pubsub_topic,
        request_scope_max_width_preference=request_scope_max_width_preference,
        require_customer_visible_justification=args.require_customer_visible_justification,
        approval_policy=approval_policy,
        update_mask=','.join(update_mask),
    )
