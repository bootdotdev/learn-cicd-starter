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
"""Imports data into a Cloud SQL instance from a TDE file.

Imports data into a Cloud SQL instance from a TDE backup file in Google Cloud
Storage.
"""


import textwrap

from googlecloudsdk.api_lib.sql import api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.sql import flags
from googlecloudsdk.command_lib.sql import import_util
from googlecloudsdk.core.console import console_io


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA,
                    base.ReleaseTrack.ALPHA)
class Tde(base.Command):
  """Import TDE certificate into a Cloud SQL for SQL Server instance."""

  detailed_help = {
      'DESCRIPTION':
          textwrap.dedent("""\
          {command} imports a TDE certificate into a Cloud SQL instance from a certificate file
          in Google Cloud Storage.

          For detailed help on importing data into Cloud SQL, refer to this
          guide: https://cloud.google.com/sql/docs/sqlserver/import-export/importing
          """),
      'EXAMPLES':
          textwrap.dedent("""\
          To import a TDE certificate with the name `foo` and certificate path `my-bucket/my-cert.cert`
          and private key path `my-bucket/my-key.pvk` and pvk password `my-pvk-password` into
          the Cloud SQL instance `my-instance`,
          run:

            $ {command} my-instance --certificate=foo --cert-path=gs://my-bucket/my-cert.cert --pvk-path=gs://my-bucket/my-key.pvk --pvk-password=my-pvk-password

          To import a TDE certificate with the name `foo` and certificate path `my-bucket/my-cert.cert`
          and private key path `my-bucket/my-key.pvk` into
          the Cloud SQL instance `my-instance` and prompting for the
          private key password,
          run:

            $ {command} my-instance --certificate=foo --cert-path=gs://my-bucket/my-cert.cert --pvk-path=gs://my-bucket/my-key.pvk --prompt-for-pvk-password
          """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddInstanceArgument(parser)
    flags.AddTdeFlags(parser)

  def Run(self, args):
    """Runs the command to import into the Cloud SQL instance."""
    if args.prompt_for_pvk_password:
      args.pvk_password = console_io.PromptPassword('Private Key Password: ')

    client = api_util.SqlClient(api_util.API_VERSION_DEFAULT)
    return import_util.RunTdeImportCommand(args, client)
