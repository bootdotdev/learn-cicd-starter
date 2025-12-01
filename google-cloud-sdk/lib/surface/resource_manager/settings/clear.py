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
"""Unset-value command for the Resource Settings CLI."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.resource_manager.settings import utils as api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.resource_manager.settings import arguments
from googlecloudsdk.command_lib.resource_manager.settings import utils
from googlecloudsdk.core.console import console_io


@base.Hidden
@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Clear(base.DescribeCommand):
  r"""Remove the value of a resource setting.

  Remove the value of a resource setting. This reverts the resource to
  inheriting the resource settings from above it in the resource hierarchy,
  if any is set on a resource above it.

  ## EXAMPLES

  To unset the resource settings ``net-preferredDnsServers'' with the
  project ``foo-project'', run:

    $ {command} net-preferredDnsServers --project=foo-project
  """

  @staticmethod
  def Args(parser):
    arguments.AddSettingsNameArgToParser(parser)
    arguments.AddResourceFlagsToParser(parser)

  def Run(self, args):
    """Unset the resource settings.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the Args method.

    Returns:
       The deleted settings.
    """

    settings_service = api_utils.GetServiceFromArgs(args)
    setting_name = utils.GetSettingsPathFromArgs(args)

    if not console_io.PromptContinue(
        message=('Your setting will be cleared.'),
    ):
      return None

    get_request = api_utils.GetDeleteValueRequestFromArgs(args, setting_name)
    setting_value = settings_service.Clear(get_request)

    return setting_value
