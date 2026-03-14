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
"""Command to enroll a new scope."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.audit_manager import constants
from googlecloudsdk.api_lib.audit_manager import enrollments
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.audit_manager import exception_utils
from googlecloudsdk.command_lib.audit_manager import flags
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import properties


_DETAILED_HELP = {
    'DESCRIPTION': 'Enroll a new scope.',
    'EXAMPLES': """ \
        To enroll a project with ID `123` with `gs://test-bucket-1` and `gs://my-bucket-2` as eligible storage buckets, run:

        $ {command} --project=123 --eligible-gcs-buckets="gs://test-bucket-1,gs://my-bucket-2"
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Add(base.CreateCommand):
  """Enroll a new scope."""

  detailed_help = _DETAILED_HELP
  api_version = constants.ApiVersion.V1

  @staticmethod
  def Args(parser):
    flags.AddProjectOrFolderOrOrganizationFlags(parser, 'to enroll')
    flags.AddEligibleDestinationsFlags(parser)

  def Run(self, args):
    """Run the add command."""
    is_parent_folder = args.folder is not None
    is_parent_organization = args.organization is not None

    if is_parent_folder:
      scope = 'folders/{folder}'.format(folder=args.folder)
    elif is_parent_organization:
      scope = 'organizations/{organization}'.format(
          organization=args.organization
      )
    else:
      scope = 'projects/{project}'.format(project=args.project)

    scope += '/locations/global'

    client = enrollments.EnrollmentsClient(api_version=self.api_version)

    try:
      return client.Add(
          scope,
          eligible_gcs_buckets=args.eligible_gcs_buckets,
          is_parent_folder=is_parent_folder,
          is_parent_organization=is_parent_organization,
      )

    except apitools_exceptions.HttpError as error:
      exc = exception_utils.AuditManagerError(error)

      if exc.has_error_info(exception_utils.ERROR_REASON_PERMISSION_DENIED):
        role = 'roles/auditmanager.admin'
        user = properties.VALUES.core.account.Get()
        exc.suggested_command_purpose = 'grant permission'
        if is_parent_folder:
          command_prefix = (
              'gcloud resource-manager folders add-iam-policy-binding'
          )
        elif is_parent_organization:
          command_prefix = (
              'gcloud resource-manager organizations add-iam-policy-binding'
          )
        else:
          command_prefix = 'gcloud projects add-iam-policy-binding'
        exc.suggested_command = (
            f'{command_prefix}'
            f' {args.folder if is_parent_folder else args.organization if is_parent_organization else args.project}'
            f' --member=user:{user} --role {role}'
        )

      core_exceptions.reraise(exc)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AddAlpha(Add):
  """Enroll a new scope."""

  api_version = constants.ApiVersion.V1_ALPHA
