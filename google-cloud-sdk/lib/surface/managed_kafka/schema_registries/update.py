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
"""Implementation of gcloud managed kafka schema registries update command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.managed_kafka import arguments
from googlecloudsdk.command_lib.managed_kafka import util
from googlecloudsdk.core import log
from googlecloudsdk.core import resources
from googlecloudsdk.generated_clients.apis.managedkafka.v1 import managedkafka_v1_messages

PROJECTS_RESOURCE_PATH = 'projects/'
LOCATIONS_RESOURCE_PATH = 'locations/'
SCHEMA_REGISTRIES_RESOURCE_PATH = 'schemaRegistries/'


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update the mode and compatibility of a schema registry.

  ## EXAMPLES

  Modify the mode of the schema registry to READONLY:

    $ {command} --mode=READONLY

  Modify the compatibility of the schema registry to BACKWARDS:

    $ {command} --compatibility=BACKWARDS
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    arguments.AddSchemaRegistryArgToParser(parser)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--mode',
        type=str,
        help='The mode of the schema registry to update.',
    )
    group.add_argument(
        '--compatibility',
        type=str,
        help='The compatibility of the schema registry to update.',
    )

  def Run(self, args):
    """Called when the user runs gcloud managed-kafka schema-registries update ...

    Args:
      args: all the arguments that were provided to this command invocation.

    Returns:
      The updated schema registry.
    """

    client = apis.GetClientInstance('managedkafka', 'v1')
    message = client.MESSAGES_MODULE

    project_id = util.ParseProject(args.project)
    location = args.location
    schema_registry_resource = resources.REGISTRY.Parse(
        args.schema_registry,
        collection='managedkafka.projects.locations.schemaRegistries',
        params={
            'projectsId': project_id,
            'locationsId': location,
            'schemaRegistriesId': args.schema_registry,
        },
    )

    schema_registry_path = schema_registry_resource.RelativeName()

    if args.mode:
      name = schema_registry_path + '/mode'
      updatemoderequest = message.UpdateSchemaModeRequest()
      updatemoderequest.mode = (
          managedkafka_v1_messages.UpdateSchemaModeRequest.ModeValueValuesEnum(
              args.mode
          )
      )
      request = message.ManagedkafkaProjectsLocationsSchemaRegistriesContextsModeUpdateRequest(
          name=name, updateSchemaModeRequest=updatemoderequest
      )
      response = (
          client.projects_locations_schemaRegistries_contexts_mode.Update(
              request=request
          )
      )
      log.UpdatedResource(
          args.schema_registry, details='mode to %s' % response.mode
      )
    if args.compatibility:
      name = schema_registry_path + '/config'
      updateconfigrequest = message.UpdateSchemaConfigRequest()
      updateconfigrequest.compatibility = managedkafka_v1_messages.UpdateSchemaConfigRequest.CompatibilityValueValuesEnum(
          args.compatibility
      )
      request = message.ManagedkafkaProjectsLocationsSchemaRegistriesContextsConfigUpdateRequest(
          name=name, updateSchemaConfigRequest=updateconfigrequest
      )
      response = (
          client.projects_locations_schemaRegistries_contexts_config.Update(
              request=request
          )
      )
      log.UpdatedResource(
          args.schema_registry,
          details='compatibility to %s' % response.compatibility,
      )
      # TODO: b/418768300 - Add normalize and alias to the output once they
      # are supported.
      log.status.Print(
          'Current schema registry config: \n - compatibility: %s'
          % (response.compatibility)
      )
