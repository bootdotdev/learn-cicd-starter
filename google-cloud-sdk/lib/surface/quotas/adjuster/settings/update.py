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
"""QuotaAdjusterSettings update command."""

import json

from apitools.base.py import encoding
from googlecloudsdk.api_lib.quotas import quota_adjuster_settings
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.quotas import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class UpdateBeta(base.UpdateCommand):
  """Update the QuotaAdjusterSettings of a resource container.

  This command updates the enablement state of a resource container.

  ## EXAMPLES

  To update QuotaAdjusterSettings for `projects/12321`, run:

    $ {command}
    --enablement=enabled
    --project=12321

  To update QuotaAdjusterSettings for `folders/123`, run:

    $ {command}
    --enablement=inherited
    --folder=123
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    # required flags
    flags.AddResourceFlags(parser, 'container id')
    flags.Enablement().AddToParser(parser)

    # optional flags
    flags.ValidateOnly().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The updated QuotaAdjusterSettings. If `--validate-only` is specified, it
      returns
      None or any possible error.
    """
    self.updated_resource = quota_adjuster_settings.UpdateQuotaAdjusterSettings(
        args, release_track=base.ReleaseTrack.BETA
    )
    self.validate_only = args.validate_only
    return self.updated_resource

  def Epilog(self, resources_were_displayed=True):
    if resources_were_displayed and not self.validate_only:
      log.status.Print(
          json.dumps(
              encoding.MessageToDict(self.updated_resource),
              sort_keys=True,
              indent=4,
              separators=(',', ':'),
          )
      )


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class UpdateAlpha(base.UpdateCommand):
  """Update the QuotaAdjusterSettings of a resource container.

  This command updates the enablement state of the resource container.

  ## EXAMPLES

  To update QuotaAdjusterSettings for `projects/12321`, run:

    $ {command}
    --enablement=Enabled
    --project=12321

    To update QuotaAdjusterSettings for `folders/123`, run:

    $ {command}
    --enablement=inherited
    --folder=123
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    # required flags
    flags.AddResourceFlags(parser, 'container id')
    flags.Enablement().AddToParser(parser)

    # optional flags
    flags.ValidateOnly().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The updated QuotaAdjusterSettings. If `--validate-only` is specified, it
      returns
      None or any possible error.
    """
    # This is because alpha gcloud points to the v1 version of the API.
    self.updated_resource = quota_adjuster_settings.UpdateQuotaAdjusterSettings(
        args, release_track=base.ReleaseTrack.GA
    )
    self.validate_only = args.validate_only
    return self.updated_resource

  def Epilog(self, resources_were_displayed=True):
    if resources_were_displayed and not self.validate_only:
      log.status.Print(
          json.dumps(
              encoding.MessageToDict(self.updated_resource),
              sort_keys=True,
              indent=4,
              separators=(',', ':'),
          )
      )
