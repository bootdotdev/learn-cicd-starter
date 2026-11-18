# -*- coding: utf-8 -*- #
# Copyright 2018 Google LLC. All Rights Reserved.
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
"""Command for spanner instances update."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import instance_operations
from googlecloudsdk.api_lib.spanner import instances
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import flags
from googlecloudsdk.command_lib.spanner import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.Command):
  """Update a Cloud Spanner instance."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To update the display name of a Cloud Spanner instance, run:

          $ {command} my-instance-id --description=my-new-display-name

        To update the node count of a Cloud Spanner instance, run:

          $ {command} my-instance-id --nodes=1
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear-
    pair for that argument which can follow the argument itself.
    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.Description(required=False).AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    resource_args.AddExpireBehaviorArg(parser)
    resource_args.AddInstanceTypeArg(parser)
    flags.AddCapacityArgsForInstance(
        require_all_autoscaling_args=False,
        parser=parser,
        add_asymmetric_option_flag=True,
        asymmetric_options_group=True,
        add_asymmetric_total_cpu_target_flag=True,
        add_asymmetric_disable_autoscaling_flags=True,
        autoscaling_cpu_target_group=True,
    )
    flags.Edition(None, True).AddToParser(parser)
    flags.DefaultBackupScheduleType(
        choices={
            'DEFAULT_BACKUP_SCHEDULE_TYPE_UNSPECIFIED': 'Not specified.',
            'NONE': (
                'No default backup schedule is created automatically when a new'
                ' database is created in an instance.'
            ),
            'AUTOMATIC': (
                'A default backup schedule is created automatically when a new'
                ' database is created in an instance. You can edit or delete'
                " the default backup schedule once it's created. The default"
                ' backup schedule creates a full backup every 24 hours. These'
                ' full backups are retained for 7 days.'
            ),
        },
    ).AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    instance_type = resource_args.GetInstanceType(args)
    expire_behavior = resource_args.GetExpireBehavior(args)

    op = instances.Patch(
        args.instance,
        description=args.description,
        nodes=args.nodes,
        processing_units=args.processing_units,
        autoscaling_min_nodes=args.autoscaling_min_nodes,
        autoscaling_max_nodes=args.autoscaling_max_nodes,
        autoscaling_min_processing_units=args.autoscaling_min_processing_units,
        autoscaling_max_processing_units=args.autoscaling_max_processing_units,
        autoscaling_high_priority_cpu_target=args.autoscaling_high_priority_cpu_target,
        autoscaling_total_cpu_target=args.autoscaling_total_cpu_target,
        autoscaling_storage_target=args.autoscaling_storage_target,
        asymmetric_autoscaling_options=args.asymmetric_autoscaling_option,
        clear_asymmetric_autoscaling_options=args.clear_asymmetric_autoscaling_option,
        instance_type=instance_type,
        expire_behavior=expire_behavior,
        edition=args.edition,
        default_backup_schedule_type=args.default_backup_schedule_type,
    )
    if args.async_:
      return op
    instance_operations.Await(op, 'Updating instance')


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class BetaUpdate(base.Command):
  """Update a Cloud Spanner instance."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To update the display name of a Cloud Spanner instance, run:

          $ {command} my-instance-id --description=my-new-display-name

        To update the node count of a Cloud Spanner instance, run:

          $ {command} my-instance-id --nodes=1
        """),
  }

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear-
    pair for that argument which can follow the argument itself.
    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.Description(required=False).AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    resource_args.AddExpireBehaviorArg(parser)
    resource_args.AddInstanceTypeArg(parser)
    flags.AddCapacityArgsForInstance(
        require_all_autoscaling_args=False,
        parser=parser,
        add_asymmetric_option_flag=True,
        asymmetric_options_group=True,
        add_asymmetric_total_cpu_target_flag=True,
        add_asymmetric_disable_autoscaling_flags=True,
        autoscaling_cpu_target_group=True,
        add_disable_downscaling_flag=True,
    )
    flags.Edition(None, True).AddToParser(parser)
    flags.DefaultBackupScheduleType(
        choices={
            'DEFAULT_BACKUP_SCHEDULE_TYPE_UNSPECIFIED': 'Not specified.',
            'NONE': (
                'No default backup schedule is created automatically when a new'
                ' database is created in an instance.'
            ),
            'AUTOMATIC': (
                'A default backup schedule is created automatically when a new'
                ' database is created in an instance. You can edit or delete'
                " the default backup schedule once it's created. The default"
                ' backup schedule creates a full backup every 24 hours. These'
                ' full backups are retained for 7 days.'
            ),
        },
    ).AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    instance_type = resource_args.GetInstanceType(args)
    expire_behavior = resource_args.GetExpireBehavior(args)

    op = instances.Patch(
        args.instance,
        description=args.description,
        nodes=args.nodes,
        processing_units=args.processing_units,
        autoscaling_min_nodes=args.autoscaling_min_nodes,
        autoscaling_max_nodes=args.autoscaling_max_nodes,
        autoscaling_min_processing_units=args.autoscaling_min_processing_units,
        autoscaling_max_processing_units=args.autoscaling_max_processing_units,
        autoscaling_high_priority_cpu_target=args.autoscaling_high_priority_cpu_target,
        autoscaling_total_cpu_target=args.autoscaling_total_cpu_target,
        autoscaling_storage_target=args.autoscaling_storage_target,
        asymmetric_autoscaling_options=args.asymmetric_autoscaling_option,
        disable_downscaling=args.disable_downscaling,
        clear_asymmetric_autoscaling_options=args.clear_asymmetric_autoscaling_option,
        instance_type=instance_type,
        expire_behavior=expire_behavior,
        edition=args.edition,
        default_backup_schedule_type=args.default_backup_schedule_type,
    )
    if args.async_:
      return op
    instance_operations.Await(op, 'Updating instance')


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaUpdate(base.Command):
  """Update a Cloud Spanner instance with ALPHA features."""

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To update the display name of a Cloud Spanner instance, run:

          $ {command} my-instance-id --description=my-new-display-name

        To update the node count of a Cloud Spanner instance, run:

          $ {command} my-instance-id --nodes=1
        """),
  }

  __doc__ = Update.__doc__

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command.

    Please add arguments in alphabetical order except for no- or a clear-
    pair for that argument which can follow the argument itself.
    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
    """
    flags.Instance().AddToParser(parser)
    flags.Description(required=False).AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    resource_args.AddExpireBehaviorArg(parser)
    resource_args.AddInstanceTypeArg(parser)
    flags.AddCapacityArgsForInstance(
        require_all_autoscaling_args=False,
        parser=parser,
        add_asymmetric_option_flag=True,
        asymmetric_options_group=True,
        autoscaling_cpu_target_group=True,
        add_asymmetric_total_cpu_target_flag=True,
        add_asymmetric_disable_autoscaling_flags=True,
        add_disable_downscaling_flag=True,
    )

    flags.SsdCache().AddToParser(parser)
    flags.Edition(None, True).AddToParser(parser)
    flags.DefaultBackupScheduleType(
        choices={
            'DEFAULT_BACKUP_SCHEDULE_TYPE_UNSPECIFIED': 'Not specified.',
            'NONE': (
                'No default backup schedule is created automatically when a new'
                ' database is created in an instance.'
            ),
            'AUTOMATIC': (
                'A default backup schedule is created automatically when a new'
                ' database is created in an instance. You can edit or delete'
                " the default backup schedule once it's created. The default"
                ' backup schedule creates a full backup every 24 hours. These'
                ' full backups are retained for 7 days.'
            ),
        },
    ).AddToParser(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    instance_type = resource_args.GetInstanceType(args)
    expire_behavior = resource_args.GetExpireBehavior(args)

    op = instances.Patch(
        args.instance,
        description=args.description,
        nodes=args.nodes,
        processing_units=args.processing_units,
        autoscaling_min_nodes=args.autoscaling_min_nodes,
        autoscaling_max_nodes=args.autoscaling_max_nodes,
        autoscaling_min_processing_units=args.autoscaling_min_processing_units,
        autoscaling_max_processing_units=args.autoscaling_max_processing_units,
        autoscaling_high_priority_cpu_target=args.autoscaling_high_priority_cpu_target,
        autoscaling_total_cpu_target=args.autoscaling_total_cpu_target,
        autoscaling_storage_target=args.autoscaling_storage_target,
        asymmetric_autoscaling_options=args.asymmetric_autoscaling_option,
        disable_downscaling=args.disable_downscaling,
        clear_asymmetric_autoscaling_options=args.clear_asymmetric_autoscaling_option,
        instance_type=instance_type,
        expire_behavior=expire_behavior,
        ssd_cache_id=args.ssd_cache,
        edition=args.edition,
        default_backup_schedule_type=args.default_backup_schedule_type,
    )
    if args.async_:
      return op
    instance_operations.Await(op, 'Updating instance')
