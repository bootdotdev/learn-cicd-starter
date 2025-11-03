# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""Command for spanner instances get-locations."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
import textwrap
from googlecloudsdk.api_lib.spanner import instances
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import flags


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Move(base.Command):
  """Move the Cloud Spanner instance to the specified instance configuration."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To move the Cloud Spanner instance, which has two CMEK-enabled
          databases db1 and db2 and a database db3 with Google-managed
          encryption keys, to the target instance configuration nam3
          (us-east4, us-east1, us-central1), run:
          $ gcloud spanner instances move my-instance-id
            --target-config=nam3
            --target-database-move-configs=^:^database-id=db1:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
            --target-database-move-configs=^:^database-id=db2:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    For `move` command, we have one positional argument, `instanceId`

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.TargetConfig().AddToParser(parser)
    parser.add_argument(
        '--target-database-move-configs',
        metavar='^:^database-id=DATABASE_ID:kms-key-names=KEY1,KEY2',
        type=arg_parsers.ArgObject(
            spec={
                'database-id': str,
                'kms-key-names': str,
            },
            required_keys=['database-id'],
            repeated=True,
        ),
        action=arg_parsers.FlattenAction(),
        help=(
            'Database level configurations for each database to be moved.'
            ' Currently only used for CMEK-enabled databases to specificy the'
            ' target database KMS keys.'
        ),
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. From `Args`, we extract command line
        arguments
    """
    instances.Move(
        args.instance, args.target_config, args.target_database_move_configs
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class BetaMove(base.Command):
  """Move the Cloud Spanner instance to the specified instance configuration."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To move the Cloud Spanner instance, which has two CMEK-enabled
          databases db1 and db2 and a database db3 with Google-managed
          encryption keys, to the target instance configuration nam3
          (us-east4, us-east1, us-central1), run:
          $ gcloud beta spanner instances move my-instance-id
            --target-config=nam3
            --target-database-move-configs=^:^database-id=db1:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
            --target-database-move-configs=^:^database-id=db2:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    For `move` command, we have one positional argument, `instanceId`

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.TargetConfig().AddToParser(parser)
    parser.add_argument(
        '--target-database-move-configs',
        metavar='^:^database-id=DATABASE_ID:kms-key-names=KEY1,KEY2',
        type=arg_parsers.ArgObject(
            spec={
                'database-id': str,
                'kms-key-names': str,
            },
            required_keys=['database-id'],
            repeated=True,
        ),
        action=arg_parsers.FlattenAction(),
        help=(
            'Database level configurations for each database to be moved.'
            ' Currently only used for CMEK-enabled databases to specificy the'
            ' target database KMS keys.'
        ),
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. From `Args`, we extract command line
        arguments
    """
    instances.Move(
        args.instance, args.target_config, args.target_database_move_configs
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaMove(base.Command):
  """Move the Cloud Spanner instance to the specified instance configuration."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
          To move the Cloud Spanner instance, which has two CMEK-enabled
          databases db1 and db2 and a database db3 with Google-managed
          encryption keys, to the target instance configuration nam3
          (us-east4, us-east1, us-central1), run:
          $ gcloud alpha spanner instances move my-instance-id
            --target-config=nam3
            --target-database-move-configs=^:^database-id=db1:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
            --target-database-move-configs=^:^database-id=db2:kms-key-names=projects/myproject/locations/us-east4/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-east1/keyRings/mykeyring/cryptoKeys/cmek-key,projects/myproject/locations/us-central1/keyRings/mykeyring/cryptoKeys/cmek-key
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    For `move` command, we have one positional argument, `instanceId`

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.TargetConfig().AddToParser(parser)
    parser.add_argument(
        '--target-database-move-configs',
        metavar='^:^database-id=DATABASE_ID:kms-key-names=KEY1,KEY2',
        type=arg_parsers.ArgObject(
            spec={
                'database-id': str,
                'kms-key-names': str,
            },
            required_keys=['database-id'],
            repeated=True,
        ),
        action=arg_parsers.FlattenAction(),
        help=(
            'Database level configurations for each database to be moved.'
            ' Currently only used for CMEK-enabled databases to specificy the'
            ' target database KMS keys.'
        ),
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. From `Args`, we extract command line
        arguments
    """
    instances.Move(
        args.instance, args.target_config, args.target_database_move_configs
    )
