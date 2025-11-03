# -*- coding: utf-8 -*- #
# Copyright 2020 Google LLC. All Rights Reserved.
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
"""Command to create a datastream private connection."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.datastream import private_connections
from googlecloudsdk.api_lib.datastream import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.datastream import flags
from googlecloudsdk.command_lib.datastream import resource_args
from googlecloudsdk.command_lib.datastream.private_connections import flags as pc_flags
from googlecloudsdk.command_lib.util.concepts import concept_parsers
from googlecloudsdk.command_lib.util.concepts import presentation_specs


DESCRIPTION = ('Create a Datastream private connection')
EXAMPLES = """\
    To create a privateConnection with VPC Peering called 'my-privateConnection', run:

        $ {command} my-privateConnection --location=us-central1 --display-name=my-privateConnection --vpc=vpc-example --subnet=10.0.0.0/29

    To create a privateConnection with PSC Interface called 'my-privateConnection', run:

        $ {command} my-privateConnection --location=us-central1 --display-name=my-privateConnection --network-attachment=network-attachment-example
   """
EXAMPLES_BETA = """\
    To create a privateConnection with VPC Peering called 'my-privateConnection', run:

        $ {command} my-privateConnection --location=us-central1 --display-name=my-privateConnection --vpc-name=vpc-example --subnet=10.0.0.0/29


   """


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Create(base.Command):
  """Create a Datastream private connection."""
  detailed_help = {'DESCRIPTION': DESCRIPTION, 'EXAMPLES': EXAMPLES}

  @staticmethod
  def CommonArgs(parser, release_track):
    """Common arguments for all release tracks.

    Args:
      parser: An argparse parser that you can use to add arguments that go on
        the command line after this command. Positional arguments are allowed.
      release_track: Some arguments are added based on the command release
        track.
    """
    resource_args.AddPrivateConnectionResourceArg(parser, 'to create')
    pc_flags.AddDisplayNameFlag(parser)
    # pc_flags.AddNetworkAttachmentFlag(parser)
    pc_flags.AddValidateOnlyFlag(parser)
    flags.AddLabelsCreateFlags(parser)

    config_group = parser.add_group(mutex=True, required=True)

    vpc_peering_group = config_group.add_group(
        help='Arguments for VPC Peering configuration.'
    )
    vpc_peering_group.add_argument(
        '--subnet',
        help="""A free subnet for peering. (CIDR of /29).""",
        required=True,
    )

    # Add VPC resource arg inside the VPC Peering group
    vpc_field_name = 'vpc'
    if release_track == base.ReleaseTrack.BETA:
      vpc_field_name = 'vpc-name'

    vpc_spec = presentation_specs.ResourcePresentationSpec(
        '--%s' % vpc_field_name,
        resource_args.GetVpcResourceSpec(),
        'Resource ID of the VPC network to peer with.',
        required=True,
    )  # Ensure VPC is required within this group
    concept_parsers.ConceptParser([vpc_spec]).AddToParser(vpc_peering_group)

    # --- PSC Interface Group ---
    if release_track == base.ReleaseTrack.GA:
      psc_group = config_group.add_group(
          help='Arguments for Private Service Connect Interface configuration.'
      )
      pc_flags.AddNetworkAttachmentFlag(psc_group)

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command."""
    Create.CommonArgs(parser, base.ReleaseTrack.GA)

  def Run(self, args):
    """Create a Datastream private connection.

    Args:
      args: argparse.Namespace, The arguments that this command was invoked
        with.

    Returns:
      A dict object representing the operations resource describing the create
      operation if the create was successful.
    """
    private_connection_ref = args.CONCEPTS.private_connection.Parse()
    parent_ref = private_connection_ref.Parent().RelativeName()

    pc_client = private_connections.PrivateConnectionsClient()
    result_operation = pc_client.Create(
        parent_ref, private_connection_ref.privateConnectionsId,
        self.ReleaseTrack(), args)

    client = util.GetClientInstance()
    messages = util.GetMessagesModule()
    resource_parser = util.GetResourceParser()

    operation_ref = resource_parser.Create(
        'datastream.projects.locations.operations',
        operationsId=result_operation.name,
        projectsId=private_connection_ref.projectsId,
        locationsId=private_connection_ref.locationsId)

    return client.projects_locations_operations.Get(
        messages.DatastreamProjectsLocationsOperationsGetRequest(
            name=operation_ref.operationsId))


@base.Deprecate(
    is_removed=False,
    warning=('Datastream beta version is deprecated. Please use`gcloud '
             'datastream private-connections create` command instead.')
)
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  """Create a Datastream private connection."""
  detailed_help = {'DESCRIPTION': DESCRIPTION, 'EXAMPLES': EXAMPLES_BETA}

  @staticmethod
  def Args(parser):
    """Args is called by calliope to gather arguments for this command."""
    Create.CommonArgs(parser, base.ReleaseTrack.BETA)
