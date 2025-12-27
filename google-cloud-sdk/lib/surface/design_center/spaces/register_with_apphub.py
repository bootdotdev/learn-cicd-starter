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
"""Command to register deployed resources with an AppHub application using application or application template as source in a space."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import glob
import json

from googlecloudsdk.api_lib.design_center import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.design_center import flags
from googlecloudsdk.core import log


def ExtractResourceInfoFromTfstate(tfstate_path):
  """Parses a .tfstate file to extract info from resource instances.

  Args:
    tfstate_path: Path to the .tfstate file.

  Returns:
    A list of dictionaries, each containing info about a resource
    instance that has an 'id' attribute. Returns None if file cannot be read
    or parsed.
  """
  try:
    with open(tfstate_path, 'r') as f:
      data = json.load(f)
  except FileNotFoundError:
    raise exceptions.BadFileException(
        'Could not read tfstate file: {0}'.format(tfstate_path)
    )
  except json.JSONDecodeError:
    raise exceptions.BadFileException(
        'Could not parse tfstate file: {0}'.format(tfstate_path)
    )

  extracted_info = []
  resources = data.get('resources', [])

  for resource in resources:
    instances = resource.get('instances', [])
    for instance in instances:
      attributes = instance.get('attributes')
      if attributes and isinstance(attributes, dict):
        res_id = attributes.get('id')
        if res_id:
          info = {
              'id': res_id,
              'location': attributes.get('location'),
              'project': attributes.get('project'),
          }
          extracted_info.append(info)

  return extracted_info


_DETAILED_HELP = {
    'DESCRIPTION': (
        'Register deployed resources with an AppHub application using '
        'application or application template as source in a space'
    ),
    'EXAMPLES': """ \
          To register deployed resources with an AppHub application using the AppHub application URI in the space `my-space`, in the project `my-project` and location `us-central1`, run:

          $ {command} my-space --project=my-project --location=us-central1 \\
            --apphub-application-uri=`projects/my-project/locations/us-central1/applications/my-app`

          Or run using the full resource name:

            $ {command} projects/my-project/locations/us-central1/spaces/my-space \\
            --apphub-application-uri=`projects/my-project/locations/us-central1/applications/my-app`

          To register deployed resources with an AppHub application using the Application Design Center application URI in the space `my-space`, in the project `my-project` and location `us-central1`, run:

            $ {command} my-space --project=my-project --location=us-central1 \\
            --adc-application-uri=`projects/my-project/locations/us-central1/spaces/my-space/applications/my-application`

          To register deployed resources with an AppHub application using the Application Design Center application URI in the space `my-space`, in the project `my-project` and location `us-central1`, when the tfstate location is given, run:

            $ {command} my-space --project=my-project --location=us-central1 \\
            --adc-application-uri=`projects/my-project/locations/us-central1/spaces/my-space/applications/my-application` \\
            --tfstate-location=`./my-module.tfstate`
          """,
    'API REFERENCE': """ \
        This command uses the designcenter/v1alpha API. The full documentation for
        this API can be found at:
        http://cloud.google.com/application-design-center/docs
        """,
}


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
@base.UniverseCompatible
class RegisterWithApphub(base.Command):
  """Register deployed resources with an AppHub application using application or application template as source in a space."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    flags.AddRegisterWithApphubFlags(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""
    client = utils.GetClientInstance(self.ReleaseTrack())
    messages = utils.GetMessagesModule(self.ReleaseTrack())
    space_ref = args.CONCEPTS.space.Parse()

    tfstate_location = args.tfstate_location
    if not tfstate_location:
      # If no tfstate location is provided, try to discover one in the current
      # directory.
      tfstates = glob.glob('*.tfstate')
      if len(tfstates) == 1:
        tfstate_location = tfstates[0]
        log.status.Print(
            '`--tfstate-location` not provided, using discovered state file:'
            f' {tfstate_location}'
        )
      elif len(tfstates) > 1:
        raise exceptions.InvalidArgumentException(
            '--tfstate-location',
            'Multiple `.tfstate` files found in current directory:'
            f' {", ".join(tfstates)}. Please specify one using'
            ' --tfstate-location.',
        )
      else:
        raise exceptions.InvalidArgumentException(
            '--tfstate-location',
            'No .tfstate file found in current directory. Please specify one'
            ' using --tfstate-location.',
        )

    deployed_resources = []
    log.status.Print(f'Parsing tfstate file: {tfstate_location}')
    resources = ExtractResourceInfoFromTfstate(tfstate_location)
    for resource in resources:
      deployed_resources.append(
          messages.DeployedResource(
              resourceId=resource['id'],
              project=resource['project'],
              location=resource['location'],
          )
      )

    register_request = messages.RegisterApphubResourcesRequest(
        deployedResources=deployed_resources
    )
    if args.adc_application_uri:
      register_request.adcApplicationUri = args.adc_application_uri
    elif args.apphub_application_uri:
      register_request.apphubApplicationUri = args.apphub_application_uri

    request = messages.DesigncenterProjectsLocationsSpacesRegisterApphubResourcesRequest(
        parent=space_ref.RelativeName(),
        registerApphubResourcesRequest=register_request,
    )

    op = client.projects_locations_spaces.RegisterApphubResources(request)

    if args.async_:
      log.status.Print('Registration started asynchronously.')
      return op

    response = utils.WaitForOperationWithEmbeddedResult(
        client,
        op,
        'Waiting for registration to complete',
        max_wait_sec=1800,
        release_track=self.ReleaseTrack(),
    )

    log.status.Print(
        'Registration completed for AppHub application: {0}'.format(
            response['apphubApplicationUri']
        )
    )

    if response.get('registeredResources'):
      log.status.Print('Successfully registered resources:')
      for res in response['registeredResources']:
        log.status.Print('- {0}'.format(res))

    if response.get('unregisteredResources'):
      log.warning('Failed to register resources:')
      for failed_res in response['unregisteredResources']:
        log.warning(
            '- Resource: {0}, Error: {1}'.format(
                failed_res['deployedResource']['resourceId'],
                failed_res['reason'],
            )
        )

    return response
