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
"""Start the Spanner command-line interface."""

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import cli_backend
from googlecloudsdk.command_lib.spanner import flags
from googlecloudsdk.command_lib.spanner import resource_args
from googlecloudsdk.command_lib.util.apis import arg_utils
from googlecloudsdk.core import properties


DETAILED_HELP = {
    "EXAMPLES": """\
      To start an interactive shell with your Spanner example database, run the following command:

        $ {command} example-database --instance=example-instance
    """,
}


def AddBaseArgs(parser):
  """Parses provided arguments to add base arguments.

  Args:
    parser: an argparse argument parser.
  """
  resource_args.AddDatabaseResourceArg(
      parser, "to use within the interactive shell"
  )
  flags.GetSpannerCliDatabaseRoleFlag().AddToParser(parser)
  flags.GetSpannerCliDelimiterFlag().AddToParser(parser)
  flags.GetSpannerCliExecuteFlag().AddToParser(parser)
  flags.GetSpannerCliHostFlag().AddToParser(parser)
  flags.GetSpannerCliHtmlFlag().AddToParser(parser)
  flags.GetSpannerCliIdleTransactionTimeoutFlag().AddToParser(parser)
  flags.GetSpannerCliInitCommandAddFlag().AddToParser(parser)
  flags.GetSpannerCliInitCommandFlag().AddToParser(parser)
  flags.GetSpannerCliPortFlag().AddToParser(parser)
  flags.GetSpannerCliPromptFlag().AddToParser(parser)
  flags.GetSpannerCliSkipColumnNamesFlag().AddToParser(parser)
  flags.GetSpannerCliSkipSystemCommandFlag().AddToParser(parser)
  flags.GetSpannerCliSystemCommandFlag().AddToParser(parser)
  flags.GetSpannerCliSourceFlag().AddToParser(parser)
  flags.GetSpannerCliTableFlag().AddToParser(parser)
  flags.GetSpannerCliTeeFlag().AddToParser(parser)
  flags.GetSpannerCliXmlFlag().AddToParser(parser)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Cli(base.BinaryBackedCommand):
  """An interactive shell for Spanner."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """See base class."""
    AddBaseArgs(parser)

  def Run(self, args):
    project = arg_utils.GetFromNamespace(args, "--project", use_defaults=True)
    instance = args.CONCEPTS.database.Parse().Parent().Name()
    api_endpoint_override = properties.VALUES.api_endpoint_overrides.Property(
        "spanner"
    ).Get()

    # Create the command executor.
    command_executor = cli_backend.SpannerCliWrapper()
    env_vars = cli_backend.GetEnvArgsForCommand()
    command_executor(
        project=project,
        database=args.database,
        instance=instance,
        database_role=args.database_role,
        host=args.host,
        port=args.port,
        api_endpoint=api_endpoint_override,
        idle_transaction_timeout=args.idle_transaction_timeout,
        skip_column_names=args.skip_column_names,
        skip_system_command=args.skip_system_command,
        system_command=args.system_command,
        prompt=args.prompt,
        delimiter=args.delimiter,
        table=args.table,
        html=args.html,
        xml=args.xml,
        execute=args.execute,
        source=args.source,
        tee=args.tee,
        init_command=args.init_command,
        init_command_add=args.init_command_add,
        env=env_vars,
    )
    pass
