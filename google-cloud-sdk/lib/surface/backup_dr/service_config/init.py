# -*- coding: utf-8 -*- #
# Copyright 2025 Google LLC. All Rights Reserved.
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
"""Initialize a Backup and DR Service Config."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.backupdr import util
from googlecloudsdk.api_lib.backupdr.service_config import ServiceConfigClient
from googlecloudsdk.api_lib.util import exceptions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.backupdr import flags
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Init(base.Command):
  """Initialize a Backup and DR Service configuration."""

  detailed_help = {
      'BRIEF': 'Initializes a Backup and DR Service configuration.',
      'DESCRIPTION': '{description}',
      'API REFERENCE': (
          'This command uses the backupdr/v1 API. The full documentation for'
          ' this API can be found at:'
          ' https://cloud.google.com/backup-disaster-recovery'
      ),
      'EXAMPLES': """\
        To initialize a new service configuration in location ``MY_LOCATION''
        and project ``MY_PROJECT'' for resource type ``MY_RESOURCE_TYPE'', run:

        $ {command} --project=MY_PROJECT \
            --location=MY_LOCATION \
            --resource-type=MY_RESOURCE_TYPE
        """,
  }

  @staticmethod
  def Args(parser):
    """Specifies additional command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    flags.AddNoAsyncFlag(parser)
    flags.AddLocationResourceArg(
        parser,
        """The location for which the service configuration should be created.""",
    )
    flags.AddResourceType(
        parser,
        """The resource type to which the default service configuration
           will be applied. Examples include, "compute.<UNIVERSE_DOMAIN>.com/Instance"
""",
    )

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    client = ServiceConfigClient()
    location = args.CONCEPTS.location.Parse().RelativeName()
    resource_type = args.resource_type
    no_async = args.no_async

    try:
      operation = client.Init(
          location,
          resource_type,
      )
    except apitools_exceptions.HttpError as e:
      raise exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)

    if no_async:
      resource = client.WaitForOperation(
          operation_ref=client.GetOperationRef(operation),
          message=(
              'Initializing service configuration for resource type [{}] in'
              ' location [{}]. (This operation could take up to 2 minutes.)'
              .format(resource_type, location)
          ),
          has_result=False,
      )

      # pylint: disable=protected-access
      # none of the log.CreatedResource, log.DeletedResource etc. matched
      log._PrintResourceChange(
          'Initialization of service configuration',
          location,
          kind='location',
          is_async=False,
          details=None,
          failed=None,
          operation_past_tense='Service configuration initialized for',
      )
      return resource

    # pylint: disable=protected-access
    # none of the log.CreatedResource, log.DeletedResource etc. matched
    log._PrintResourceChange(
        'Initialization of service configuration',
        location,
        kind='location',
        is_async=True,
        details=util.ASYNC_OPERATION_MESSAGE.format(operation.name),
        failed=None,
    )
    return operation
