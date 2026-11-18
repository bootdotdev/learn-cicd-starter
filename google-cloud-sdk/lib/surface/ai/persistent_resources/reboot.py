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
"""Command to reboot a Persistent Resource in Vertex AI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import re

from googlecloudsdk.api_lib.ai.persistent_resources import client
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai.persistent_resources import flags
from googlecloudsdk.command_lib.ai.persistent_resources import validation
from googlecloudsdk.core import log
from googlecloudsdk.core import properties

_OPERATION_RESOURCE_NAME_TEMPLATE = (
    'projects/{project}/locations/{region}/operations/{operation_id}')

_PERSISTENT_RESOURCE_REBOOT_DISPLAY_MESSAGE = """\
Request to reboot the PersistentResource [{name}] has been sent.

You may view the status of your PersistentResource reboot operation with the command

  $ {command_prefix} ai operations describe {operation_resource_name}

"""


@base.ReleaseTracks(base.ReleaseTrack.GA)
class RebootGA(base.SilentCommand):
  """Reboot a Persistent Resource.

  ## EXAMPLES

  To reboot a persistent resource ``123'' under project ``example'' in region
  ``us-central1'', run:

    $ {command} 123 --project=example --region=us-central1
  """
  _api_version = constants.GA_VERSION

  @staticmethod
  def Args(parser):
    flags.AddPersistentResourceResourceArg(parser, 'to reboot')

  def _CommandPrefix(self):
    cmd_prefix = 'gcloud'
    if self.ReleaseTrack().prefix:
      cmd_prefix += ' ' + self.ReleaseTrack().prefix
    return cmd_prefix

  def Run(self, args):
    persistent_resource_ref = args.CONCEPTS.persistent_resource.Parse()
    region = persistent_resource_ref.AsDict()['locationsId']
    validation.ValidateRegion(region)

    with endpoint_util.AiplatformEndpointOverrides(
        version=self._api_version, region=region):
      project = properties.VALUES.core.project.GetOrFail()
      resource_name = persistent_resource_ref.RelativeName()
      response = client.PersistentResourcesClient(
          version=self._api_version).Reboot(resource_name)

      operation_id = re.search(r'operations\/(\d+)', response.name).groups(0)[0]
      operation_resource_name = _OPERATION_RESOURCE_NAME_TEMPLATE.format(
          project=project,
          region=region,
          operation_id=operation_id,
      )

      log.status.Print(
          _PERSISTENT_RESOURCE_REBOOT_DISPLAY_MESSAGE.format(
              name=resource_name,
              command_prefix=self._CommandPrefix(),
              operation_resource_name=operation_resource_name))
      return response


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class RebootPreGA(RebootGA):
  """Reboot an active Persistent Resource.

  ## EXAMPLES

  To reboot a persistent resource ``123'' under project ``example'' in region
  ``us-central1'', run:

    $ {command} 123 --project=example --region=us-central1
  """
  _api_version = constants.BETA_VERSION
