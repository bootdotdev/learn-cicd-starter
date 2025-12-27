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
"""The gcloud run presets describe command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import pkgutil

from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.run import exceptions as run_exceptions
from googlecloudsdk.command_lib.run.printers import presets_printer
from googlecloudsdk.core import exceptions
from googlecloudsdk.core import yaml
from googlecloudsdk.core.resource import resource_printer


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Describe(base.DescribeCommand):
  """Describe a Cloud Run preset. Currently only available in alpha."""

  detailed_help = {
      'DESCRIPTION': """
          {description}
      """,
      'EXAMPLES': """
          To describe a preset, run:

            $ {command} <preset-name>
      """,
  }

  @staticmethod
  def Args(parser):
    parser.add_argument(
        'name',
        help='The name of the preset to describe.')
    resource_printer.RegisterFormatter(
        presets_printer.PRESETS_PRINTER_FORMAT,
        presets_printer.PresetsPrinter,
        hidden=True,
    )
    parser.display_info.AddFormat(presets_printer.PRESETS_PRINTER_FORMAT)

  def Run(self, args):
    """Returns the preset metadata details for the given preset name."""
    try:
      # TODO(b/414798340): Modify this when PresetMetadata design is finalized.
      presets_yaml_contents = pkgutil.get_data(
          'googlecloudsdk.command_lib.run', 'presets.yaml')
      presets_data = yaml.load(presets_yaml_contents)

    except IOError:
      raise exceptions.Error('Presets file not found.')

    for preset in presets_data.get('presets', []):
      if preset.get('name') == args.name:
        return preset

    raise run_exceptions.ArgumentError(f"Preset '{args.name}' not found.")
