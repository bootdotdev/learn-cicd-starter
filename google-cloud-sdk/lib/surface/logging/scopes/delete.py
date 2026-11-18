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

"""'logging scopes delete' command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import base
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io


@base.UniverseCompatible
class Delete(base.DeleteCommand):
  """Delete a log scope.

  ## EXAMPLES

  To delete a log scope, run:

    $ {command} my-scope
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('LOG_SCOPE_ID', help='ID of the log scope to delete.')
    util.AddParentArgs(
        parser, 'log scope to delete', exclude_billing_account=True
    )
    parser.display_info.AddCacheUpdater(None)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.
    """
    console_io.PromptContinue(
        'Really delete log scope [%s]? (You can not recover it after deletion)'
        % args.LOG_SCOPE_ID,
        cancel_on_no=True,
    )

    util.GetClient().projects_locations_logScopes.Delete(
        util.GetMessages().LoggingProjectsLocationsLogScopesDeleteRequest(
            name=util.CreateResourceName(
                util.CreateResourceName(
                    util.GetParentFromArgs(args, exclude_billing_account=True),
                    'locations',
                    'global',
                ),
                'logScopes',
                args.LOG_SCOPE_ID,
            )
        )
    )
    log.DeletedResource(args.LOG_SCOPE_ID)
