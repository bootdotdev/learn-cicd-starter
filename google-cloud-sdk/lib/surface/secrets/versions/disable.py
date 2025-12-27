# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Disable the version of the provided secret."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.secrets import api as secrets_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.secrets import args as secrets_args
from googlecloudsdk.command_lib.secrets import log as secrets_log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Disable(base.DeleteCommand):
  r"""Disable the version of the provided secret.

  Disable the version of the provided secret. It can be re-enabled with
  `{parent_command} enable`.

  ## EXAMPLES

  Disable version `123` of the secret named `my-secret`:

    $ {command} 123 --secret=my-secret

  Disable version `123` of the secret named `my-secret` using etag:

    $ {command} 123 --secret=my-secret --etag=123
  """

  @staticmethod
  def Args(parser):
    secrets_args.AddVersion(
        parser, purpose='to disable', positional=True, required=True
    )
    secrets_args.AddLocation(parser, purpose='to disable', hidden=False)
    secrets_args.AddVersionEtag(parser, action='disabled')

  def Run(self, args):
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    version_ref = args.CONCEPTS.version.Parse()
    result = secrets_api.Versions(api_version=api_version).Disable(
        version_ref, etag=args.etag, secret_location=args.location
    )
    secrets_log.Versions().Disabled(version_ref)
    return result


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class DisableBeta(Disable):
  r"""Disable the version of the provided secret.

  Disable the version of the provided secret. It can be re-enabled with
  `{parent_command} enable`.

  ## EXAMPLES

  Disable version `123` of the secret named `my-secret`:

    $ {command} 123 --secret=my-secret

  Disable version `123` of the secret named `my-secret` using an etag:

    $ {command} 123 --secret=my-secret --etag=123
  """

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    """Args is called by calliope to gather arguments for secrets versions disable command.

    Args:
      parser: An argparse parser that you can use to add arguments that will be
        available to this command.
    """
    secrets_args.AddVersion(
        parser, purpose='to disable', positional=True, required=True
    )
    secrets_args.AddLocation(parser, purpose='to disable', hidden=False)
    secrets_args.AddVersionEtag(parser, action='disabled')

  def Run(self, args: parser_extensions.Namespace) -> secrets_api.Versions:
    """Run is called by calliope to implement the secret versions disable command.

    Args:
      args: an argparse namespace, all the arguments that were provided to this
        command invocation.

    Returns:
      API call to invoke secret version disable.
    """
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    version_ref = args.CONCEPTS.version.Parse()
    result = secrets_api.Versions(api_version=api_version).Disable(
        version_ref, etag=args.etag, secret_location=args.location
    )
    secrets_log.Versions().Disabled(version_ref)
    return result
