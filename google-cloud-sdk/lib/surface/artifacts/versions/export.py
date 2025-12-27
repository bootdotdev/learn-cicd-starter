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
"""Export an Artifact Registry version."""

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
@base.Hidden
class Export(base.Command):
  """Export an Artifact Registry package version.

  Export files of an Artifact Registry package version to a Google Cloud Storage
  path.
  """

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
      To export version `1.0.0` of package `my-pkg` to a Google Cloud Storage path `gs://my-bucket/sub-folder` under the current project, repository, and location, run:

          $ {command} 1.0.0 --package=my-pkg --gcs-destination=gs://my-bucket/sub-folder
  """,
  }

  @staticmethod
  def Args(parser):
    """Set up arguments for this command.

    Args:
      parser: An argparse.Parser.
    """
    flags.GetRequiredVersionFlag().AddToParser(parser)
    parser.add_argument(
        '--gcs-destination',
        metavar='GCS_DESTINATION',
        required=True,
        help='Google Cloud Storage path to export the artifact to.',
    )

  def Run(self, args):
    """Run the export command."""
    version_ref = args.CONCEPTS.version.Parse()
    # ExportArtifact takes the gcs_destination path without the "gs://" prefix.
    # We allow the "gs://" prefix here to match yum/apt/googet import commands.
    gcs_destination = args.gcs_destination.removeprefix('gs://')
    op = requests.ExportArtifact(version_ref, None, gcs_destination)
    op_ref = resources.REGISTRY.ParseRelativeName(
        op.name, collection='artifactregistry.projects.locations.operations'
    )
    log.status.Print(
        'Export request issued from [{}] to [{}].\nCreated operation [{}].'
        .format(
            version_ref.RelativeName(),
            args.gcs_destination,
            op_ref.RelativeName(),
        )
    )
