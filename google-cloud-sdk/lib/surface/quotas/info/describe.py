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
"""QuotaInfo get command."""

from googlecloudsdk.api_lib.quotas import quota_info
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.quotas import flags


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class DescribeAlpha(base.DescribeCommand):
  """Retrieve the QuotaInfo of a quota for a project, folder or organization.

  ## EXAMPLES

  To get the details about quota `CpusPerProject` for service
  `example.$$UNIVERSE_DOMAIN$$` and `projects/my-project`, run:

    $ {command} CpusPerProject --service=example.$$UNIVERSE_DOMAIN$$
    --project=my-project


  To get the details about quota `CpusPerProject` for service
  `example.$$UNIVERSE_DOMAIN$$` and `folders/123`, run:

    $ {command} CpusPerProject --service=example.$$UNIVERSE_DOMAIN$$
    --folder=123
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.QuotaId().AddToParser(parser)
    flags.AddResourceFlags(parser, 'quota info to describe')
    flags.Service().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The requested QuotaInfo for specified container and service.
    """
    # This is because alpha gcloud points to GA version of the API.
    return quota_info.GetQuotaInfo(
        args.project,
        args.folder,
        args.organization,
        args.service,
        args.QUOTA_ID,
        release_track=base.ReleaseTrack.GA,
    )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class DescribeBeta(base.DescribeCommand):
  """Retrieve the QuotaInfo of a quota for a project, folder or organization.

  ## EXAMPLES

  To get the details about quota `CpusPerProject` for service
  `example.$$UNIVERSE_DOMAIN$$` and `projects/my-project`, run:

    $ {command} CpusPerProject --service=example.$$UNIVERSE_DOMAIN$$
    --project=my-project


  To get the details about quota `CpusPerProject` for service
  `example.$$UNIVERSE_DOMAIN$$` and `folders/123`, run:

    $ {command} CpusPerProject --service=example.$$UNIVERSE_DOMAIN$$
    --folder=123
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.QuotaId().AddToParser(parser)
    flags.AddResourceFlags(parser, 'quota info to describe')
    flags.Service().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The requested QuotaInfo for specified container and service.
    """
    return quota_info.GetQuotaInfo(
        args.project,
        args.folder,
        args.organization,
        args.service,
        args.QUOTA_ID,
        release_track=base.ReleaseTrack.BETA,
    )
