# -*- coding: utf-8 -*- #
# Copyright 2024 Google LLC. All Rights Reserved.
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
"""Implementation of gcloud dataflow yaml run command."""

from googlecloudsdk.api_lib.dataflow import apis
from googlecloudsdk.api_lib.storage import storage_api
from googlecloudsdk.api_lib.storage import storage_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataflow import dataflow_util
from googlecloudsdk.core import properties
from googlecloudsdk.core import yaml
from googlecloudsdk.core.util import files


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.BETA)
class Run(base.Command):
  """Runs a job from the specified path."""

  detailed_help = {
      'DESCRIPTION': (
          'Runs a job from the specified YAML description or '
          'Cloud Storage path.'
      ),
      'EXAMPLES': """\
          To run a job from YAML, run:

            $ {command} my-job --yaml-pipeline-file=gs://yaml-path --region=europe-west1
          """,
  }

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: argparse.ArgumentParser to register arguments with.
    """
    parser.add_argument(
        'job_name', metavar='JOB_NAME', help='Unique name to assign to the job.'
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--yaml-pipeline-file',
        help=(
            'Path of a file defining the YAML pipeline to run. '
            "(Must be a local file or a URL beginning with 'gs://'.)"
        ),
    )

    group.add_argument(
        '--yaml-pipeline', help='Inline definition of the YAML pipeline to run.'
    )

    parser.add_argument(
        '--region',
        metavar='REGION_ID',
        help=(
            "Region ID of the job's regional endpoint. "
            + dataflow_util.DEFAULT_REGION_MESSAGE
        ),
    )

    parser.add_argument(
        '--pipeline-options',
        metavar='OPTIONS=VALUE;OPTION=VALUE',
        type=arg_parsers.ArgDict(),
        action=arg_parsers.UpdateAction,
        help='Pipeline options to pass to the job.',
    )

    parser.add_argument(
        '--jinja-variables',
        metavar='JSON_OBJECT',
        help='Jinja2 variables to be used in reifying the yaml.',
    )

    parser.add_argument(
        '--template-file-gcs-location',
        help=('Google Cloud Storage location of the YAML template to run. '
              "(Must be a URL beginning with 'gs://'.)"),
        type=arg_parsers.RegexpValidator(r'^gs://.*',
                                         'Must begin with \'gs://\''),
    )

    parser.add_argument(
        '--network',
        help=(
            'Compute Engine network for launching worker instances to run '
            'the pipeline.  If not set, the default network is used.'
        ),
    )

    parser.add_argument(
        '--subnetwork',
        help=(
            'Compute Engine subnetwork for launching worker instances to '
            'run the pipeline.  If not set, the default subnetwork is used.'
        ),
    )

  def Run(self, args):
    """Runs the command.

    Args:
      args: The arguments that were provided to this command invocation.

    Returns:
      A Job message.
    """
    parameters = dict(args.pipeline_options or {})

    # These are required and mutually exclusive due to the grouping above.
    if args.yaml_pipeline_file:
      yaml_contents = _try_get_yaml_contents(args.yaml_pipeline_file)
      if yaml_contents is None:
        parameters['yaml_pipeline_file'] = args.yaml_pipeline_file
      else:
        parameters['yaml_pipeline'] = yaml_contents

    else:
      parameters['yaml_pipeline'] = args.yaml_pipeline

    if args.jinja_variables:
      parameters['jinja_variables'] = args.jinja_variables

    if 'yaml_pipeline' in parameters and 'jinja-variables' not in parameters:
      _validate_yaml(parameters['yaml_pipeline'])

    region_id = _get_region_from_yaml_or_default(
        parameters.get('yaml_pipeline'), args
    )

    gcs_location = (
        args.template_file_gcs_location
        or apis.Templates.YAML_TEMPLATE_GCS_LOCATION.format(region_id)
    )

    arguments = apis.TemplateArguments(
        project_id=properties.VALUES.core.project.Get(required=True),
        region_id=region_id,
        job_name=args.job_name,
        gcs_location=gcs_location,
        parameters=parameters,
        network=args.network,
        subnetwork=args.subnetwork,
    )
    return apis.Templates.CreateJobFromFlexTemplate(arguments)


def _validate_yaml(yaml_pipeline):
  # TODO(b/320740846): Do more complete validation without requiring importing
  # the entire beam library.
  try:
    _ = yaml.load(yaml_pipeline)
  except Exception as exn:
    raise ValueError('yaml_pipeline must be a valid yaml.') from exn


def _get_region_from_yaml_or_default(yaml_pipeline, args):
  """Gets the region from yaml pipeline or args, or falls back to default."""
  region = args.region
  options_region = None
  try:
    pipeline_data = yaml.load(yaml_pipeline)
    if not pipeline_data:
      return dataflow_util.GetRegion(args)
    if 'options' in pipeline_data and 'region' in pipeline_data['options']:
      options_region = pipeline_data['options']['region']
      if '{' in options_region or '}' in options_region:
        raise yaml.YAMLParseError(
            'yaml pipeline contains unparsable region: {0}. Found curly braces '
            'in region. Falling back to default region.'.format(options_region)
        )
  except yaml.YAMLParseError as exn:
    if not region:
      print(
          'Failed to get region from yaml pipeline: {0}. If using jinja '
          'variables, parsing may fail. Falling back to default '
          'region.'.format(exn)
      )

  if options_region:
    if region and region != options_region:
      raise ValueError(
          'Region specified in yaml pipeline options ({0}) does not match'
          ' region specified in command line ({1})'.format(
              options_region, region
          )
      )
    return options_region

  return dataflow_util.GetRegion(args)


def _try_get_yaml_contents(yaml_pipeline_file):
  """Reads yaml contents from the specified file if it is accessable."""
  if not yaml_pipeline_file.startswith('gs://'):
    return files.ReadFileContents(yaml_pipeline_file)

  storage_client = storage_api.StorageClient()
  obj_ref = storage_util.ObjectReference.FromUrl(yaml_pipeline_file)
  try:
    return storage_client.ReadObject(obj_ref).read().decode('utf-8')
  except Exception as e:  # pylint: disable=broad-exception-caught
    print(
        'Unable to read file {0} due to incorrect file path or insufficient'
        ' read permissions. Will not be able to validate the yaml pipeline or'
        ' determine the region from the yaml pipeline'
        ' options. Error: {1}'.format(yaml_pipeline_file, e)
    )

  return None
