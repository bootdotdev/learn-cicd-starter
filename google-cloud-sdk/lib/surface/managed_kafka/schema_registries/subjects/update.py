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
"""Implementation of gcloud managed kafka schema registries subjects update command."""

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
SUBJECTS_RESOURCE_PATH = 'subjects/'
CONTEXTS_RESOURCE_PATH = '/contexts/'


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Update(base.UpdateCommand):
  """Update the mode and compatibility of a subject.

  ## EXAMPLES

  Modify the mode of the subject to READONLY:

    $ {command} --registry=SCHEMA_REGISTRY --context=CONTEXT
    --project=PROJECT_ID --location=LOCATION_ID --mode=READONLY

  Modify the compatibility of the subject to BACKWARDS:

    $ {command} --registry=SCHEMA_REGISTRY --context=CONTEXT
    --project=PROJECT_ID --location=LOCATION_ID --compatibility=BACKWARDS
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""

    arguments.AddSubjectArgToParser(parser)

    parser.add_argument(
        '--context',
        type=str,
        help='The context of the subject.',
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--mode',
        type=str,
        help='The mode of the subject to update.',
    )
    group.add_argument(
        '--compatibility',
        type=str,
        help='The compatibility of the subject to update.',
    )
    group.add_argument(
        '--delete-mode',
        action='store_true',
        help='Delete the mode of the subject.',
    )
    group.add_argument(
        '--delete-config',
        action='store_true',
        help='Delete the config of the subject.',
    )

  def Run(self, args):
    """Called when the user runs gcloud managed-kafka schema-registries subjects update ...

    Args:
      args: all the arguments that were provided to this command invocation.

    Returns:
      The updated subject.
    """

    client = apis.GetClientInstance('managedkafka', 'v1')
    message = client.MESSAGES_MODULE

    project_id = util.ParseProject(args.project)
    location = args.location
    schema_registry_id = args.registry
    subject = args.CONCEPTS.subject.Parse().subjectsId
    subject_run_resource = resources.REGISTRY.Parse(
        args.subject,
        collection='managedkafka.projects.locations.schemaRegistries.subjects',
        params={
            'projectsId': project_id,
            'locationsId': location,
            'schemaRegistriesId': schema_registry_id,
            'subjectsId': subject,
        },
    )
    schema_registry_resource = subject_run_resource.Parent().RelativeName()
    if args.context:
      schema_registry_resource = (
          f'{schema_registry_resource}{CONTEXTS_RESOURCE_PATH}{args.context}'
      )

    if args.delete_config:
      util.DeleteSubjectConfig(subject, schema_registry_resource, args.context)

    if args.delete_mode:
      util.DeleteSubjectMode(subject, schema_registry_resource, args.context)

    if args.mode:
      mode = args.mode.upper()
      name = f'{schema_registry_resource}/mode/{args.CONCEPTS.subject.Parse().subjectsId}'
      updatemoderequest = message.UpdateSchemaModeRequest()
      updatemoderequest.mode = (
          managedkafka_v1_messages.UpdateSchemaModeRequest.ModeValueValuesEnum(
              mode
          )
      )
      # Check if context is provided.
      if args.context:
        request = message.ManagedkafkaProjectsLocationsSchemaRegistriesContextsModeUpdateRequest(
            name=name, updateSchemaModeRequest=updatemoderequest
        )
        response = (
            client.projects_locations_schemaRegistries_contexts_mode.Update(
                request=request
            )
        )
      else:
        request = message.ManagedkafkaProjectsLocationsSchemaRegistriesModeUpdateRequest(
            name=name, updateSchemaModeRequest=updatemoderequest
        )
        response = client.projects_locations_schemaRegistries_mode.Update(
            request=request
        )

      log.UpdatedResource(subject, details='mode to %s' % response.mode)

    if args.compatibility:
      compatibility = args.compatibility.upper()
      name = f'{schema_registry_resource}/config/{args.CONCEPTS.subject.Parse().subjectsId}'
      updateconfigrequest = message.UpdateSchemaConfigRequest()
      updateconfigrequest.compatibility = managedkafka_v1_messages.UpdateSchemaConfigRequest.CompatibilityValueValuesEnum(
          compatibility
      )
      # Check if context is provided.
      if args.context:
        request = message.ManagedkafkaProjectsLocationsSchemaRegistriesContextsConfigUpdateRequest(
            name=name, updateSchemaConfigRequest=updateconfigrequest
        )
        response = (
            client.projects_locations_schemaRegistries_contexts_config.Update(
                request=request
            )
        )
      else:
        request = message.ManagedkafkaProjectsLocationsSchemaRegistriesConfigUpdateRequest(
            name=name, updateSchemaConfigRequest=updateconfigrequest
        )
        response = client.projects_locations_schemaRegistries_config.Update(
            request=request
        )

      log.UpdatedResource(
          subject, details='compatibility to %s' % response.compatibility
      )

      # TODO: b/418768300 - Add normalize and alias to the output once they
      # are supported.
      log.status.Print(
          'Current subject config: \n - compatibility: %s'
          % (response.compatibility)
      )
