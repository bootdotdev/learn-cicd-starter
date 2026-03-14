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
"""Command for spanner instance partitions update."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import textwrap

from googlecloudsdk.api_lib.spanner import instance_partition_operations
from googlecloudsdk.api_lib.spanner import instance_partitions
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.spanner import flags
from googlecloudsdk.command_lib.spanner import resource_args


@base.DefaultUniverseOnly
@base.ReleaseTracks(
    base.ReleaseTrack.GA, base.ReleaseTrack.BETA
)
class Update(base.Command):
  """Update a Spanner instance partition. You can't update the default instance partition using this command."""  # pylint: disable=line-too-long

  detailed_help = {
      'EXAMPLES': textwrap.dedent("""\
        To update the display name of a Spanner instance partition, run:

          $ {command} my-instance-partition-id --instance=my-instance-id --description=my-new-display-name

        To update the node count of a Spanner instance partition, run:

          $ {command} my-instance-partition-id --instance=my-instance-id --nodes=1
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
    resource_args.AddInstancePartitionResourceArg(parser, 'to update')
    flags.Description(
        required=False, text='Description of the instance partition.'
    ).AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddCapacityArgsForInstancePartition(
        parser=parser,
        add_autoscaling_args=True,
        autoscaling_args_hidden=True,
        require_all_autoscaling_args=False,
    )

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    op = instance_partitions.Patch(
        args.CONCEPTS.instance_partition.Parse(),
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
    )
    if args.async_:
      return op
    return instance_partition_operations.Await(
        op, 'Updating instance partition'
    )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class AlphaUpdate(Update):
  """Update a Spanner instance partition with ALPHA features."""

  __doc__ = Update.__doc__

  @staticmethod
  def Args(parser):
    """See base class."""
    resource_args.AddInstancePartitionResourceArg(parser, 'to update')
    flags.Description(
        required=False, text='Description of the instance partition.'
    ).AddToParser(parser)
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddCapacityArgsForInstancePartition(
        parser=parser,
        add_autoscaling_args=True,
        autoscaling_args_hidden=True,
        require_all_autoscaling_args=False,
    )

  def Run(self, args):
    """See base class."""
    op = instance_partitions.Patch(
        args.CONCEPTS.instance_partition.Parse(),
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
    )
    if args.async_:
      return op
    return instance_partition_operations.Await(
        op, 'Updating instance partition'
    )
