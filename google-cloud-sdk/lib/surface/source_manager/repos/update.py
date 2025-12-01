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
"""Update Secure Source Manager repository command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.securesourcemanager import repositories
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.source_manager import flags
from googlecloudsdk.command_lib.source_manager import resource_args
from googlecloudsdk.core import log

DETAILED_HELP = {
    "DESCRIPTION": """
          Update a Secure Source Manager repository.
        """,
    "EXAMPLES": """
            To update the description of a repository called `my-repo` in
            location `us-central1`, run the following command:

            $ {command} my-repo --description="new description" --region=us-central1
        """,
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
class Update(base.UpdateCommand):
  """Update a Secure Source Manager repository."""

  NO_CHANGES_MESSAGE = (
      "There are no changes to the repository [{repository}] for update"
  )

  @staticmethod
  def Args(parser):
    resource_args.AddRepositoryResourceArg(parser, "to update")
    flags.AddDescription(parser)
    flags.AddValidateOnly(parser)

  def Run(self, args):
    # Get resource args to contruct base url
    repository_ref = args.CONCEPTS.repository.Parse()
    # Update repository
    client = repositories.RepositoriesClient()

    # Collect the list of update masks
    update_mask = []
    if args.IsSpecified("description"):
      update_mask.append("description")

    if not update_mask:
      raise exceptions.MinimumArgumentException(
          [
              "--description",
          ],
          self.NO_CHANGES_MESSAGE.format(repository=repository_ref.Name()),
      )

    # this is a shortcut LRO, it completes immediately and is marked as done
    # there is no need to wait
    update_operation = client.Update(
        repository_ref, update_mask, args.validate_only, args.description
    )
    log.UpdatedResource(repository_ref.RelativeName())
    return update_operation


Update.detailed_help = DETAILED_HELP
