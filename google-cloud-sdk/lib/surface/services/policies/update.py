# -*- coding: utf-8 -*- #
# Copyright 2025 Google Inc. All Rights Reserved.
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
"""services policies update command."""

from googlecloudsdk.api_lib.services import exceptions
from googlecloudsdk.api_lib.services import services_util
from googlecloudsdk.api_lib.services import serviceusage
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.services import common_flags
from googlecloudsdk.core import yaml


# TODO(b/321801975) make command public after suv2 launch.
@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(base.Command):
  """Update consumer policy for a project, folder or organization.

  Update consumer policy for a project, folder or organization.

  ## EXAMPLES

  Update consumer policy

   $ {command} --consumer-policy-file=/path/to/the/file.yaml

  Validate the update action on the policy:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml --validate-only

  Update consumer policy and bypass dependency check:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml
   --bypass-dependency-check

  Update consumer policy and bypass api usage check:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml
   --bypass-api-usage-check
  """

  @staticmethod
  def Args(parser):
    common_flags.consumer_policy_file_flag().AddToParser(parser)
    common_flags.validate_only_args(parser, suffix='to update')
    common_flags.bypass_api_usage_check().AddToParser(parser)
    common_flags.bypass_dependency_check().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Response from longrunning.operations from UpdateConsumerPolicy API call.
    """

    if not args.consumer_policy_file.endswith('.yaml'):
      raise exceptions.ConfigError(
          'Invalid consumer_policy_file format. Please provide path to a yaml'
          ' file.'
      )

    policy = yaml.load_path(args.consumer_policy_file)

    if not isinstance(policy, dict):
      raise exceptions.ConfigError(
          'Invalid consumer-policy-file. Please provide a valid policy.'
      )

    if 'name' not in policy:
      raise exceptions.ConfigError(
          'Invalid Consumer Policy. Please provide a name.'
      )

    op = serviceusage.UpdateConsumerPolicy(
        policy,
        validate_only=args.validate_only,
        bypass_dependency_check=args.bypass_dependency_check,
        force=args.bypass_api_usage_check,
    )

    op = services_util.WaitOperation(op.name, serviceusage.GetOperationV2Beta)
    if args.validate_only:
      services_util.PrintOperation(op)
    else:
      services_util.PrintOperationWithResponseForUpdateConsumerPolicy(op)


# TODO(b/321801975) make command public after suv2 launch.
@base.UniverseCompatible
@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Update(base.Command):
  """Update consumer policy for a project, folder or organization.

  Update consumer policy for a project, folder or organization.

  ## EXAMPLES

  Update consumer policy

   $ {command} --consumer-policy-file=/path/to/the/file.yaml

  Validate the update action on the policy:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml --validate-only

  Update consumer policy and bypass dependency check:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml
   --bypass-dependency-check

  Update consumer policy and bypass api usage check:

   $ {command} --consumer-policy-file=/path/to/the/file.yaml
   --bypass-api-usage-check
  """

  @staticmethod
  def Args(parser):
    common_flags.consumer_policy_file_flag().AddToParser(parser)
    common_flags.validate_only_args(parser, suffix='to update')
    common_flags.bypass_api_usage_check().AddToParser(parser)
    common_flags.bypass_dependency_check().AddToParser(parser)

  def Run(self, args):
    """Run command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Response from longrunning.operations from UpdateConsumerPolicy API call.
    """

    if not args.consumer_policy_file.endswith('.yaml'):
      raise exceptions.ConfigError(
          'Invalid consumer_policy_file format. Please provide path to a yaml'
          ' file.'
      )

    policy = yaml.load_path(args.consumer_policy_file)

    if not isinstance(policy, dict):
      raise exceptions.ConfigError(
          'Invalid consumer-policy-file. Please provide a valid policy.'
      )

    if 'name' not in policy:
      raise exceptions.ConfigError(
          'Invalid Consumer Policy. Please provide a name.'
      )

    op = serviceusage.UpdateConsumerPolicy(
        policy,
        validate_only=args.validate_only,
        bypass_dependency_check=args.bypass_dependency_check,
        force=args.bypass_api_usage_check,
    )

    op = services_util.WaitOperation(op.name, serviceusage.GetOperationV2Beta)
    if args.validate_only:
      services_util.PrintOperation(op)
    else:
      services_util.PrintOperationWithResponseForUpdateConsumerPolicy(op)
