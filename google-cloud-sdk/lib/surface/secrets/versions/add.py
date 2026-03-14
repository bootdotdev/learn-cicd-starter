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
"""Enable the version of the provided secret."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.secrets import api as secrets_api
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.calliope import parser_arguments
from googlecloudsdk.calliope import parser_extensions
from googlecloudsdk.command_lib.secrets import args as secrets_args
from googlecloudsdk.command_lib.secrets import log as secrets_log
from googlecloudsdk.command_lib.secrets import util as secrets_util
from googlecloudsdk.command_lib.util import crc32c


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.CreateCommand):
  r"""Create a new version of an existing secret.

  Create a new version of an existing secret with the provided data. The
  command will return an error if no such secret exists.

  ## EXAMPLES

  Create a new version of an existing secret named 'my-secret' with secret data
  "s3cr3t":

    $ printf "s3cr3t" | {command} my-secret --data-file=-

  Create a new version of an existing secret named 'my-secret' with secret data
  "s3cr3t" using PowerShell (Note: PowerShell will add a newline to the
  resulting secret):

    $ Write-Output "s3cr3t" | {command} my-secret --data-file=-

  Create a new version of an existing secret named 'my-secret' with secret data
  from a file:

    $ {command} my-secret --data-file=/tmp/secret
  """

  EMPTY_DATA_FILE_MESSAGE = (
      'The value provided for --data-file is the empty string. This can happen '
      'if you pass or pipe a variable that is undefined. Please verify that '
      'the --data-file flag is not the empty string.')

  @staticmethod
  def Args(parser: parser_arguments.ArgumentInterceptor):
    """Args is called by calliope to gather arguments for secrets versions add command.

    Args:
      parser: An argparse parser that you can use to add arguments that will be
        available to this command.
    """
    secrets_args.AddSecret(
        parser, purpose='to create', positional=True, required=True
    )
    secrets_args.AddLocation(
        parser, purpose='to create secret version', hidden=False
    )
    secrets_args.AddDataFile(parser, required=True)

  def Run(self, args: parser_extensions.Namespace) -> secrets_api.Versions:
    """Run is called by calliope to implement the secret versions add command.

    Args:
      args: an argparse namespace, all the arguments that were provided to this
        command invocation.

    Returns:
      API call to invoke secret version add.
    """
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    secret_ref = args.CONCEPTS.secret.Parse()
    is_regional = args.location is not None
    data = secrets_util.ReadFileOrStdin(args.data_file)

    # Differentiate between the flag being provided with an empty value and the
    # flag being omitted. See b/138796299 for info.
    if args.data_file == '':  # pylint: disable=g-explicit-bool-comparison
      raise exceptions.BadFileException(self.EMPTY_DATA_FILE_MESSAGE)

    data_crc32c = crc32c.get_crc32c(data)
    version = secrets_api.Secrets(api_version=api_version).AddVersion(
        secret_ref,
        data,
        crc32c.get_checksum(data_crc32c),
        secret_location=args.location,
    )
    if is_regional:
      version_ref = secrets_args.ParseRegionalVersionRef(version.name)
    else:
      version_ref = secrets_args.ParseVersionRef(version.name)
    secrets_log.Versions().Created(version_ref)
    if not version.clientSpecifiedPayloadChecksum:
      raise exceptions.HttpException(
          'Version created but payload data corruption may have occurred, '
          'please destroy the created version, and retry. See also '
          'https://cloud.google.com/secret-manager/docs/data-integrity.'
      )
    return version


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  r"""Create a new version of an existing secret.

  Create a new version of an existing secret with the provided data. The
  command will return an error if no such secret exists.

  ## EXAMPLES

  Create a new version of an existing secret named 'my-secret' with secret data
  "s3cr3t":

    $ printf "s3cr3t" | {command} my-secret --data-file=-

  Create a new version of an existing secret named 'my-secret' with secret data
  "s3cr3t" using PowerShell (Note: PowerShell will add a newline to the
  resulting secret):

    $ Write-Output "s3cr3t" | {command} my-secret --data-file=-

  Create a new version of an existing secret named 'my-secret' with secret data
  from a file:

    $ {command} my-secret --data-file=/tmp/secret
  """

  @staticmethod
  def Args(parser):
    secrets_args.AddSecret(
        parser, purpose='to create', positional=True, required=True
    )
    secrets_args.AddLocation(
        parser, purpose='to create secret version', hidden=False
    )
    secrets_args.AddDataFile(parser, required=True)

  def Run(self, args):
    api_version = secrets_api.GetApiFromTrack(self.ReleaseTrack())
    secret_ref = args.CONCEPTS.secret.Parse()
    is_regional = args.location is not None
    data = secrets_util.ReadFileOrStdin(args.data_file)

    # Differentiate between the flag being provided with an empty value and the
    # flag being omitted. See b/138796299 for info.
    if args.data_file == '':  # pylint: disable=g-explicit-bool-comparison
      raise exceptions.BadFileException(self.EMPTY_DATA_FILE_MESSAGE)

    data_crc32c = crc32c.get_crc32c(data)
    version = secrets_api.Secrets(api_version=api_version).AddVersion(
        secret_ref,
        data,
        crc32c.get_checksum(data_crc32c),
        secret_location=args.location,
    )
    if is_regional:
      version_ref = secrets_args.ParseRegionalVersionRef(version.name)
    else:
      version_ref = secrets_args.ParseVersionRef(version.name)
    secrets_log.Versions().Created(version_ref)
    if not version.clientSpecifiedPayloadChecksum:
      raise exceptions.HttpException(
          'Version created but payload data corruption may have occurred, '
          'please destroy the created version, and retry. See also '
          'https://cloud.google.com/secret-manager/docs/data-integrity.')
    return version
