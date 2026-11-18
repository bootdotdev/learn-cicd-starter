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
"""Get default service account command."""

from googlecloudsdk.api_lib.cloudbuild import cloudbuild_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.builds import flags
from googlecloudsdk.core import properties


@base.UniverseCompatible
class GetDefaultServiceAccount(base.Command):
  """Get the default service account for a project."""

  detailed_help = {
      'DESCRIPTION': 'Get the default service account for a project.',
      'EXAMPLES': """
            To get the default service account for the project:

                $ {command}
            """,
  }

  @staticmethod
  def Args(parser):
    flags.AddRegionFlag(parser)
    parser.display_info.AddFormat('value(serviceAccountEmail.segment(3))')

  def Run(self, args):
    serviceaccount_region = (
        args.region
        or properties.VALUES.builds.region.Get()
        or cloudbuild_util.DEFAULT_REGION
    )
    client = cloudbuild_util.GetClientInstance()
    return client.projects_locations.GetDefaultServiceAccount(
        client.MESSAGES_MODULE.CloudbuildProjectsLocationsGetDefaultServiceAccountRequest(
            name='projects/%s/locations/%s/defaultServiceAccount'
            % (
                properties.VALUES.core.project.GetOrFail(),
                serviceaccount_region,
            )
        )
    )
