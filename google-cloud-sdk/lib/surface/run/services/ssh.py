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
"""Command to SSH into a Cloud Run Service."""

from googlecloudsdk.api_lib.run import ssh as run_ssh
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
@base.DefaultUniverseOnly
class Ssh(base.Command):
  """SSH into an instance."""

  detailed_help = {
      'DESCRIPTION': """\
          Starts a secure, interactive shell session with a Cloud Run instance.
          """,
      'EXAMPLES': """\
          To start an interactive shell session with a Cloud Run service:

              $ {command} my-service --instance=my-instance-id
          """,
  }

  @classmethod
  def Args(cls, parser):
    # Add flags for targeting a specific instance and container.
    flags.AddInstanceArg(parser)
    flags.AddContainerArg(parser)
    # Add the service name as a required positional argument.
    parser.add_argument(
        'service',
        help='The name of the service to SSH into.',
    )

  def Run(self, args):
    """Connect to a running Cloud Run Service deployment."""
    args.project = flags.GetProjectID(args)
    args.region = flags.GetRegion(args, prompt=False)
    if not args.region:
      raise exceptions.ArgumentError(
          'Missing required argument [region]. Set --region flag or set'
          ' run/region property.'
      )
    args.deployment_name = args.service
    args.release_track = self.ReleaseTrack()
    run_ssh.Ssh(args, run_ssh.Ssh.WorkloadType.SERVICE).Run()
