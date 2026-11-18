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
"""QuotaPreference list command."""

from googlecloudsdk.api_lib.quotas import quota_preference
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.quotas import flags


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class ListAlpha(base.ListCommand):
  """List QuotaPreferences in a given project, folder or organization.

  ## EXAMPLES

  To list the quota preferences for `projects/12321`, run:

    $ {command} --project=12321
    $ {command} --project=my-project-id


  To list first 10 quota preferences ordered by create time for `folder/123`,
  run:

    $ {command} --folder=123 --page-size=10 --sort-by=create_time


  To list all quota preferences in unresolved state in region `us-central1` for
  `organization/789`, run:

    $ {command} --organization=789 --filter=dimensions.region:us-central1
    --reconciling-only
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.AddResourceFlags(parser, 'quota preferences to list')
    flags.ReconcilingOnly().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      List of quota preferences.
    """
    # This is because alpha gcloud points to GA version of the API.
    return quota_preference.ListQuotaPreferences(
        args, release_track=base.ReleaseTrack.GA
    )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class ListBeta(base.ListCommand):
  """List QuotaPreferences in a given project, folder or organization.

  ## EXAMPLES

  To list the quota preferences for `projects/12321`, run:

    $ {command} --project=12321
    $ {command} --project=my-project-id


  To list first 10 quota preferences ordered by create time for `folder/123`,
  run:

    $ {command} --folder=123 --page-size=10 --sort-by=create_time


  To list all quota preferences in unresolved state in region `us-central1` for
  `organization/789`, run:

    $ {command} --organization=789 --filter=dimensions.region:us-central1
    --reconciling-only
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.AddResourceFlags(parser, 'quota preferences to list')
    flags.ReconcilingOnly().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      List of quota preferences.
    """
    return quota_preference.ListQuotaPreferences(
        args, release_track=base.ReleaseTrack.BETA
    )
