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
"""Implementation of gcloud managed kafka schema registries subjects describe command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.managed_kafka import arguments
from googlecloudsdk.command_lib.managed_kafka import util
from googlecloudsdk.core import log
from googlecloudsdk.core import resources

PROJECTS_RESOURCE_PATH = 'projects/'
LOCATIONS_RESOURCE_PATH = 'locations/'
SCHEMA_REGISTRIES_RESOURCE_PATH = 'schemaRegistries/'
SUBJECTS_RESOURCE_PATH = '/subjects/'
CONTEXTS_RESOURCE_PATH = '/contexts/'

SUBJECT_FORMAT = """
    table(
      subject:format='yaml(compatibility, subject.compatibility, mode, subject.mode, name, subject.name)'
    )
"""


class _Results(object):
  """Encapsulate results into a single object to fit the Run() model."""

  def __init__(self, subject):
    self.subject = subject


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class Describe(base.DescribeCommand):
  """Describe a subject in a schema registry with all of its fields.

  ## EXAMPLES

   Describe the subject in a schema registry with all of its fields:

    $ {command} --project=PROJECT_ID --location=LOCATION_ID
    --registry=SCHEMA_REGISTRY_ID
  """

  @staticmethod
  def Args(parser):
    """Register flags for this command."""

    parser.display_info.AddFormat(SUBJECT_FORMAT)

    parser.add_argument(
        '--context',
        type=str,
        help='The context of the subject.',
    )

    arguments.AddSubjectArgToParser(parser)

  def Run(self, args):
    """Called when the user runs gcloud managed-kafka schema-registries subjects describe ...

    Args:
      args: all the arguments that were provided to this command invocation.

    Returns:
      The subject.
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
    subject_resource_path = subject_run_resource.RelativeName()
    if args.context:
      subject_resource_path = f'{schema_registry_resource}{CONTEXTS_RESOURCE_PATH}{args.context}{SUBJECTS_RESOURCE_PATH}{subject}'
      schema_registry_resource = (
          f'{schema_registry_resource}{CONTEXTS_RESOURCE_PATH}{args.context}'
      )

    log.status.Print('Describing subject [{}].'.format(subject) + '\n')

    subject_mode_request = (
        message.ManagedkafkaProjectsLocationsSchemaRegistriesModeGetRequest(
            name=f'{schema_registry_resource}/mode/{subject}'
        )
    )
    subject_config_request = (
        message.ManagedkafkaProjectsLocationsSchemaRegistriesConfigGetRequest(
            name=f'{schema_registry_resource}/config/{subject}'
        )
    )

    mode = 'None'
    compatibility = 'None'
    try:
      subject_mode = client.projects_locations_schemaRegistries_mode.Get(
          request=subject_mode_request
      )
      mode = util.ParseMode(subject_mode.mode)
    except apitools_exceptions.HttpNotFoundError as e:
      api_error = exceptions.HttpException(e, util.HTTP_ERROR_FORMAT)
      if 'Resource not found' in api_error.message:
        raise exceptions.HttpException(
            e, error_format='Subject {} not found.'.format(subject)
        )
      try:
        schema_registry_mode_request = (
            message.ManagedkafkaProjectsLocationsSchemaRegistriesModeGetRequest(
                name=f'{schema_registry_resource}/mode'
            )
        )
        schema_registry_mode = (
            client.projects_locations_schemaRegistries_mode.Get(
                request=schema_registry_mode_request
            )
        )
        mode = util.ParseMode(schema_registry_mode.mode)
        mode = f'{mode} (from registry)'
      except apitools_exceptions.HttpNotFoundError as inner_e:
        # Should not happen.
        raise exceptions.HttpException(inner_e)

    try:
      subject_config = client.projects_locations_schemaRegistries_config.Get(
          request=subject_config_request,
      )
      compatibility = util.ParseCompatibility(subject_config.compatibility)
    except apitools_exceptions.HttpNotFoundError:
      try:
        schema_registry_config_request = message.ManagedkafkaProjectsLocationsSchemaRegistriesConfigGetRequest(
            name=f'{schema_registry_resource}/config'
        )
        schema_registry_config = (
            client.projects_locations_schemaRegistries_config.Get(
                request=schema_registry_config_request,
            )
        )
        compatibility = util.ParseCompatibility(
            schema_registry_config.compatibility
        )
        compatibility = f'{compatibility} (from registry)'
      except apitools_exceptions.HttpNotFoundError as inner_e:
        # Should not happen.
        raise exceptions.HttpException(inner_e)

    verbose_subject = {
        'name': subject_resource_path,
        'mode': mode,
        'compatibility': compatibility,
    }

    return _Results(verbose_subject)
