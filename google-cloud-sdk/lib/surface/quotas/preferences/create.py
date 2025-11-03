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
"""QuotaPreference create command."""

import json

from apitools.base.py import encoding
from googlecloudsdk.api_lib.quotas import quota_preference
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.quotas import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class CreateAlpha(base.CreateCommand):
  """Create a new QuotaPreference that declares the desired value for a quota.

  ## EXAMPLES

  To create a quota preference in region `us-central1` that applies to the
  `default_limit` quota under service `example.$$UNIVERSE_DOMAIN$$` for
  `projects/12321`, run:

    $ {command}
    --service=example.$$UNIVERSE_DOMAIN$$
    --project=12321
    --quota-id=default_limit
    --preferred-value=100
    --dimensions=region=us-central1
    --preference-id=example_default-limit_us-central1


  To create a quota preference under service `example.$$UNIVERSE_DOMAIN$$` for
  `organizations/789` with random preference ID, run:

    $ {command}
    --service=example.$$UNIVERSE_DOMAIN$$
    --organization=789
    --quota-id=default_limit
    --preferred-value=200
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    # required flags
    flags.AddResourceFlags(parser, 'quota preference to create')
    flags.Service().AddToParser(parser)
    flags.PreferredValue().AddToParser(parser)
    flags.QuotaId(positional=False).AddToParser(parser)

    # optional flags
    flags.PreferenceId(positional=False).AddToParser(parser)
    flags.Dimensions().AddToParser(parser)
    flags.AllowsQuotaDecreaseBelowUsage().AddToParser(parser)
    flags.AllowHighPercentageQuotaDecrease().AddToParser(parser)
    flags.Email().AddToParser(parser)
    flags.Justification().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The created quota preference.
    """
    # This is because alpha gcloud points to GA version of the API.
    self.created_resource = quota_preference.CreateQuotaPreference(
        args, release_track=base.ReleaseTrack.GA
    )
    return self.created_resource

  def Epilog(self, resources_were_displayed: bool = True):
    if resources_were_displayed:
      log.status.Print(
          json.dumps(
              encoding.MessageToDict(self.created_resource),
              sort_keys=True,
              indent=4,
              separators=(',', ':'),
          )
      )


@base.ReleaseTracks(base.ReleaseTrack.BETA)
@base.UniverseCompatible
class CreateBeta(base.CreateCommand):
  """Create a new QuotaPreference that declares the desired value for a quota.

  ## EXAMPLES

  To create a quota preference in region `us-central1` that applies to the
  `default_limit` quota under service `example.$$UNIVERSE_DOMAIN$$` for
  `projects/12321`, run:

    $ {command}
    --service=example.$$UNIVERSE_DOMAIN$$
    --project=12321
    --quota-id=default_limit
    --preferred-value=100
    --dimensions=region=us-central1
    --preference-id=example_default-limit_us-central1


  To create a quota preference under service `example.$$UNIVERSE_DOMAIN$$`` for
  `organizations/789` with random preference ID, run:

    $ {command}
    --service=example.$$UNIVERSE_DOMAIN$$
    --organization=789
    --quota-id=default_limit
    --preferred-value=200
  """

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    # Required flags.
    flags.AddResourceFlags(parser, 'quota preference to create')
    flags.Service().AddToParser(parser)
    flags.PreferredValue().AddToParser(parser)
    flags.QuotaId(positional=False).AddToParser(parser)

    # optional flags
    flags.PreferenceId(positional=False).AddToParser(parser)
    flags.Dimensions().AddToParser(parser)
    flags.AllowsQuotaDecreaseBelowUsage().AddToParser(parser)
    flags.AllowHighPercentageQuotaDecrease().AddToParser(parser)
    flags.Email().AddToParser(parser)
    flags.Justification().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      The created quota preference.
    """

    self.created_resource = quota_preference.CreateQuotaPreference(
        args, release_track=base.ReleaseTrack.BETA
    )
    return self.created_resource

  def Epilog(self, resources_were_displayed=True):
    if resources_were_displayed:
      log.status.Print(
          json.dumps(
              encoding.MessageToDict(self.created_resource),
              sort_keys=True,
              indent=4,
              separators=(',', ':'),
          )
      )
