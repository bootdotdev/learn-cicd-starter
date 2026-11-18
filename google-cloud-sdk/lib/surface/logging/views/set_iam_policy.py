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
"""'logging views set_iam_policy' command.

Set the IAM policy for a logging view resource.

This command replaces the existing IAM policy for an logging view resource,
given a file encoded in JSON or YAML that contains the IAM policy.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.logging import util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.iam import iam_util

DETAILED_HELP = {
    'DESCRIPTION': """
        Set an IAM policy for a view.
    """,
    'EXAMPLES': """
        To set the IAM policy using a json file 'my_policy.json' for the view `my-view` in `my-bucket` in the `global` location, run:

        $ {command} my-view /path/to/my_policy.json --bucket=my-bucket --location=global
    """,
}


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class SetIamPolicy(base.Command):
  """Set IAM policy for a view."""

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    parser.add_argument('VIEW_ID', help='ID of the view to set IAM policy.')
    util.AddParentArgs(parser, 'view to set IAM policy')
    util.AddBucketLocationArg(
        parser, True, 'Location of the bucket that contains the view.'
    )
    parser.add_argument(
        '--bucket',
        required=True,
        type=arg_parsers.RegexpValidator(r'.+', 'must be non-empty'),
        help='ID of the bucket that contains the view.',
    )
    iam_util.AddArgForPolicyFile(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      The IAM policy.
    """
    view = util.CreateResourceName(
        util.CreateResourceName(
            util.GetBucketLocationFromArgs(args), 'buckets', args.bucket
        ),
        'views',
        args.VIEW_ID,
    )
    messages = util.GetMessages()
    policy, _ = iam_util.ParseYamlOrJsonPolicyFile(
        args.policy_file, messages.Policy
    )
    results = util.SetIamPolicy(view, policy)
    iam_util.LogSetIamPolicy(view, 'logging view')
    return results


SetIamPolicy.detailed_help = DETAILED_HELP
