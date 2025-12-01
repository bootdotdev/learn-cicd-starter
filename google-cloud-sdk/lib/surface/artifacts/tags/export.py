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
"""Export an Artifact Registry tag."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.artifacts import flags
from googlecloudsdk.command_lib.artifacts import requests
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Export(base.Command):
  """Export an Artifact Registry package version by tag.

  Export files of an Artifact Registry package version by tag to a Google Cloud
  Storage path.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
      To export by tag `t1` of package `my-pkg` to a Google Cloud Storage path `gs://my-bucket/sub-folder` under the current project, repository, and location, run:

          $ {command} t1 --package=my-pkg --gcs-destination=gs://my-bucket/sub-folder
  """,
  }

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.Parser.
    """
    flags.GetRequiredTagFlag().AddToParser(parser)
    parser.add_argument(
        '--gcs-destination',
        metavar='GCS_DESTINATION',
        required=True,
        help='Google Cloud Storage path to export the artifact to.',
    )

  def Run(self, args):
    """Run the export command."""
    tag_ref = args.CONCEPTS.tag.Parse()
    # ExportArtifact takes the gcs_destination path without the "gs://" prefix.
    # We allow the "gs://" prefix here to match yum/apt/googet import commands.
    gcs_destination = args.gcs_destination.removeprefix('gs://')
    op = requests.ExportArtifact(None, tag_ref, gcs_destination)
    op_ref = resources.REGISTRY.ParseRelativeName(
        op.name, collection='artifactregistry.projects.locations.operations'
    )
    log.status.Print(
        'Export request issued from [{}] to [{}].\nCreated operation [{}].'
        .format(
            tag_ref.RelativeName(),
            args.gcs_destination,
            op_ref.RelativeName(),
        )
    )
