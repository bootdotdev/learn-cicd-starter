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

"""Command to export an HA Controller to a YAML file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import sys

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.ha_controllers import utils as api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.ha_controllers import utils
from googlecloudsdk.command_lib.export import util as export_util
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml
from googlecloudsdk.core.util import files


def _DetailedHelp():
  return {
      'brief':
          'Export an HA Controller.',
      'DESCRIPTION':
          """\
          Exports an High Availability (HA) Controller's configuration to a
          file. This configuration can be imported at a later time.
          """,
      'EXAMPLES':
          """\
          An HA Controller can be exported by running:

            $ {command} my-ha-controller --destination=<path-to-file>
          """
  }


def _GetApiVersion(release_track):
  """Returns the API version for the HA Controller."""
  if release_track == base.ReleaseTrack.ALPHA:
    return 'alpha'


def _GetSchemaPath(release_track, for_help=False):
  """Returns the schema path for the HA Controller."""
  return export_util.GetSchemaPath(
      'compute',
      _GetApiVersion(release_track),
      'HaController',
      for_help=for_help,
  )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Export(base.ExportCommand):
  """Export an HA Controller.

  Export an High Availability (HA) Controller, which helps
  ensure that a virtual machine (VM) instance remains operational by
  automatically managing failover across two zones.
  """

  detailed_help = _DetailedHelp()

  @staticmethod
  def Args(parser):
    utils.AddHaControllerNameArgToParser(
        parser, base.ReleaseTrack.ALPHA.name.lower()
    )
    export_util.AddExportFlags(
        parser, _GetSchemaPath(base.ReleaseTrack.ALPHA, for_help=True))

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    ha_controller_ref = args.CONCEPTS.ha_controller.Parse()
    ha_controller = api_utils.Get(client, ha_controller_ref)
    yaml_data = yaml.load(export_util.Export(
        message=ha_controller, schema_path=_GetSchemaPath(self.ReleaseTrack())
    ))
    yaml_data = utils.FixExportStructure(yaml_data)

    if args.destination:
      with files.FileWriter(args.destination) as stream:
        yaml.dump(yaml_data, stream=stream)
      return log.status.Print(
          'Exported [{}] to \'{}\'.'.format(
              ha_controller.name, args.destination
          )
      )
    else:
      yaml.dump(yaml_data, stream=sys.stdout)
