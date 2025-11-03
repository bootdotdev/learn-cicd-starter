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
"""Copy an Artifact Registry repository."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import requests
from googlecloudsdk.core import log
from googlecloudsdk.core import resources
from googlecloudsdk.core.console import progress_tracker
from googlecloudsdk.core.util import retry


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.Hidden
class Copy(base.Command):
  """Copy an Artifact Registry repository."""

  detailed_help = {
      'BRIEF': 'Copy an Artifact Registry repository.',
      'DESCRIPTION': """
          Copy all artifacts within an Artifact Registry repository to another repository.

          Note that this is pull-based, so default arguments will apply to the destination repository.
      """,
      'EXAMPLES': """\
          To copy artifacts from `repo1` in project `proj1` and location `us` to `repo2` in project `proj2` and location `asia`:

            $ {command} repo2 --project=proj2 --location=asia --source-repo=projects/proj1/locations/us/repositories/repo1
      """,
  }

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.ArgumentParser.
    """
    flags.GetRepoArg().AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    parser.add_argument(
        '--source-repo',
        metavar='SOURCE_REPOSITORY',
        required=True,
        help='The source repository path to copy artifacts from.',
    )

  def Run(self, args):
    """Run the repository copy command."""
    # Call CopyRepository API.
    client = requests.GetClient()
    repo_ref = args.CONCEPTS.repository.Parse()
    op = requests.CopyRepository(args.source_repo, repo_ref.RelativeName())
    op_ref = resources.REGISTRY.ParseRelativeName(
        op.name, collection='artifactregistry.projects.locations.operations'
    )

    # Log operation details and return if not waiting.
    log.status.Print(
        'Copy request issued from [{}] to [{}].\nCreated operation [{}].'
        .format(
            args.source_repo, repo_ref.RelativeName(), op_ref.RelativeName()
        )
    )
    if args.async_:  # Return early if --async is specified.
      return None

    # Progress tracker for polling loop.
    spinner_message = 'Copying artifacts'
    progress_info = {'copied': 0, 'total': 0}
    with progress_tracker.ProgressTracker(
        spinner_message,
        detail_message_callback=lambda: self._DetailMessage(progress_info),
        autotick=True,
    ):
      # Before polling, let user know to press CTRL-C to stop.
      log.status.Print('Press CTRL-C to stop waiting on the operation.')

      # Poll operation indefinitely.
      poller = waiter.CloudOperationPollerNoResources(
          client.projects_locations_operations
      )
      retryer = retry.Retryer(max_wait_ms=None)
      try:
        operation = retryer.RetryOnResult(
            lambda: self._PollOperation(poller, op_ref, progress_info),
            should_retry_if=lambda op, state: op and not op.done,
            sleep_ms=2000,
        )
        if operation.error:
          log.status.Print(
              '\nOperation [{}] failed: {}'.format(
                  op_ref.RelativeName(), operation.error.message
              )
          )
        return None
      except retry.WaitException:
        # This block should not be reached with max_wait_ms=None
        log.error('Error: Copy operation wait unexpectedly timed out.')
        return None
      except Exception as e:  # pylint: disable=broad-exception-caught
        log.fatal('An unexpected error occurred: {}'.format(e))
        return None

  def _DetailMessage(self, progress_info):
    """Callback to update the progress tracker message."""
    copied = progress_info['copied']
    total = progress_info['total']

    if total == 0:
      return ' operation metadata not yet available'

    progress = copied / total * 100
    return ' {:.1f}% copied ({} of {} versions)'.format(progress, copied, total)

  def _PollOperation(self, poller, op_ref, progress_info):
    """Polls the operation and updates progress_info from metadata."""
    try:
      operation = poller.Poll(op_ref)
    except waiter.PollException as e:
      # Handle potential polling errors if necessary
      log.debug('Polling error: %s', e)
      return None  # Continue polling

    if (
        operation
        and operation.metadata
        and operation.metadata.additionalProperties
    ):
      props = {p.key: p.value for p in operation.metadata.additionalProperties}
      if 'versionsCopiedCount' in props:
        progress_info['copied'] = props['versionsCopiedCount'].integer_value
      if 'totalVersionsCount' in props:
        progress_info['total'] = props['totalVersionsCount'].integer_value

    return operation
