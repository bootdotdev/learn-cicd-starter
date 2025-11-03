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
"""Model Garden deploy command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import time

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai import operations
from googlecloudsdk.api_lib.ai.model_garden import client as client_mg
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai import flags
from googlecloudsdk.command_lib.ai import model_garden_utils
from googlecloudsdk.command_lib.ai import region_util
from googlecloudsdk.command_lib.ai import validation
from googlecloudsdk.command_lib.ai.region_util import (
    _IsDefaultUniverse,
)
from googlecloudsdk.core import properties


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.UniverseCompatible
class Deploy(base.Command):
  """Deploy a model in Model Garden to a Vertex AI endpoint.

  ## EXAMPLES

  To deploy a Model Garden model `google/gemma2/gemma2-9b` under project
  `example` in region
  `us-central1`, run:

    $ gcloud ai model-garden models deploy
    --model=google/gemma2@gemma-2-9b
    --project=example
    --region=us-central1

  To deploy a Hugging Face model `meta-llama/Meta-Llama-3-8B` under project
  `example` in region `us-central1`, run:

    $ gcloud ai model-garden models deploy
    --model=meta-llama/Meta-Llama-3-8B
    --hugging-face-access-token={hf_token}
    --project=example
    --region=us-central1
  """

  @staticmethod
  def Args(parser):
    base.Argument(
        '--model',
        required=True,
        help=(
            'The model to be deployed. If it is a Model Garden model, it should'
            ' be in the format of'
            ' `{publisher_name}/{model_name}@{model_version_name}, e.g.'
            ' `google/gemma2@gemma-2-2b`. If it is a Hugging Face model, it'
            ' should be in the convention of Hugging Face models, e.g.'
            ' `meta-llama/Meta-Llama-3-8B`. If it is a Custom Weights model, it'
            ' should be in the format of `gs://{gcs_bucket_uri}`, e.g. `gs://'
            '-model-garden-public-us/llama3.1/Meta-Llama-3.1-8B-Instruct`.'
        ),
    ).AddToParser(parser)
    base.Argument(
        '--hugging-face-access-token',
        required=False,
        help=(
            'The access token from Hugging Face needed to read the'
            ' model artifacts of gated models. It is only needed when'
            ' the Hugging Face model to deploy is gated.'
        ),
    ).AddToParser(parser)
    base.Argument(
        '--endpoint-display-name',
        required=False,
        help='Display name of the endpoint with the deployed model.',
    ).AddToParser(parser)

    flags.AddRegionResourceArg(
        parser, 'to deploy the model', prompt_func=region_util.PromptForOpRegion
    )
    base.Argument(
        '--machine-type',
        help=(
            'The machine type to deploy the model to. It should be a supported'
            ' machine type from the deployment configurations of the model. Use'
            ' `gcloud ai model-garden models list-deployment-config` to check'
            ' the supported machine types.'
        ),
        required=False,
    ).AddToParser(parser)
    base.Argument(
        '--accelerator-type',
        help=(
            'The accelerator type to serve the model. It should be a supported'
            ' accelerator type from the verified deployment configurations of'
            ' the model. Use `gcloud ai model-garden models'
            ' list-deployment-config` to check the supported accelerator types.'
        ),
        required=False,
    ).AddToParser(parser)
    base.Argument(
        '--accelerator-count',
        help=(
            'The accelerator count to serve the model. Accelerator count'
            ' should be non-negative.'
        ),
        type=int,
        required=False,
    ).AddToParser(parser)
    base.Argument(
        '--accept-eula',
        help=(
            'When set, the user accepts the End User License Agreement (EULA)'
            ' of the model.'
        ),
        action='store_true',
        default=False,
        required=False,
    ).AddToParser(parser)
    base.Argument(
        '--asynchronous',
        help=(
            'If set to true, the command will terminate immediately and not'
            ' keep polling the operation status.'
        ),
        action='store_true',
        default=False,
        required=False,
    ).AddToParser(parser)
    base.Argument(
        '--reservation-affinity',
        type=arg_parsers.ArgDict(
            spec={
                'reservation-affinity-type': str,
                'key': str,
                'values': arg_parsers.ArgList(),
            },
            required_keys=['reservation-affinity-type'],
        ),
        help=(
            'A ReservationAffinity can be used to configure a Vertex AI'
            ' resource (e.g., a DeployedModel) to draw its Compute Engine'
            ' resources from a Shared Reservation, or exclusively from'
            ' on-demand capacity.'
        ),
    ).AddToParser(parser)

    base.Argument(
        '--spot',
        action='store_true',
        default=False,
        required=False,
        help='If true, schedule the deployment workload on Spot VM.',
    ).AddToParser(parser)

    base.Argument(
        '--use-dedicated-endpoint',
        action='store_true',
        default=False,
        required=False,
        help=(
            'If true, the endpoint will be exposed through a dedicated DNS.'
            ' Your request to the dedicated DNS will be isolated from other'
            " users' traffic and will have better performance and reliability."
        ),
    ).AddToParser(parser)

    base.Argument(
        '--enable-fast-tryout',
        action='store_true',
        default=False,
        required=False,
        help=(
            'If True, model will be deployed using faster deployment path.'
            ' Useful for quick experiments. Not for production workloads. Only'
            ' available for most popular models with certain machine types.'
        ),
    ).AddToParser(parser)

    base.Argument(
        '--container-image-uri',
        help=("""\
      URI of the Model serving container file in the Container Registry
      (e.g. gcr.io/myproject/server:latest).
      """),
    ).AddToParser(parser)

    parser.add_argument(
        '--container-env-vars',
        metavar='KEY=VALUE',
        type=arg_parsers.ArgDict(),
        action=arg_parsers.UpdateAction,
        help='List of key-value pairs to set as environment variables.',
    )
    parser.add_argument(
        '--container-command',
        type=arg_parsers.ArgList(),
        metavar='COMMAND',
        action=arg_parsers.UpdateAction,
        help="""\
  Entrypoint for the container image. If not specified, the container
  image's default entrypoint is run.
  """,
    )
    parser.add_argument(
        '--container-args',
        metavar='ARG',
        type=arg_parsers.ArgList(),
        help="""\
  Comma-separated arguments passed to the command run by the container
  image. If not specified and no `--command` is provided, the container
  image's default command is used.
  """,
    )
    parser.add_argument(
        '--container-ports',
        metavar='PORT',
        type=arg_parsers.ArgList(element_type=arg_parsers.BoundedInt(1, 65535)),
        action=arg_parsers.UpdateAction,
        help="""\
  Container ports to receive http requests at. Must be a number between 1 and
  65535, inclusive.
  """,
    )
    parser.add_argument(
        '--container-grpc-ports',
        metavar='PORT',
        type=arg_parsers.ArgList(element_type=arg_parsers.BoundedInt(1, 65535)),
        action=arg_parsers.UpdateAction,
        help="""\
  Container ports to receive grpc requests at. Must be a number between 1 and
  65535, inclusive.
  """,
    )
    parser.add_argument(
        '--container-predict-route',
        help='HTTP path to send prediction requests to inside the container.',
    )
    parser.add_argument(
        '--container-health-route',
        help='HTTP path to send health checks to inside the container.',
    )
    parser.add_argument(
        '--container-deployment-timeout-seconds',
        type=int,
        help='Deployment timeout in seconds.',
    )
    parser.add_argument(
        '--container-shared-memory-size-mb',
        type=int,
        help="""\
  The amount of the VM memory to reserve as the shared memory for the model in
  megabytes.
    """,
    )
    parser.add_argument(
        '--container-startup-probe-exec',
        type=arg_parsers.ArgList(),
        metavar='STARTUP_PROBE_EXEC',
        help="""\
  Exec specifies the action to take. Used by startup probe. An example of this
  argument would be ["cat", "/tmp/healthy"].
    """,
    )
    parser.add_argument(
        '--container-startup-probe-period-seconds',
        type=int,
        help="""\
  How often (in seconds) to perform the startup probe. Default to 10 seconds.
  Minimum value is 1.
    """,
    )
    parser.add_argument(
        '--container-startup-probe-timeout-seconds',
        type=int,
        help="""\
  Number of seconds after which the startup probe times out. Defaults to 1 second.
  Minimum value is 1.
    """,
    )
    parser.add_argument(
        '--container-health-probe-exec',
        type=arg_parsers.ArgList(),
        metavar='HEALTH_PROBE_EXEC',
        help="""\
  Exec specifies the action to take. Used by health probe. An example of this
  argument would be ["cat", "/tmp/healthy"].
    """,
    )
    parser.add_argument(
        '--container-health-probe-period-seconds',
        type=int,
        help="""\
  How often (in seconds) to perform the health probe. Default to 10 seconds.
  Minimum value is 1.
    """,
    )
    parser.add_argument(
        '--container-health-probe-timeout-seconds',
        type=int,
        help="""\
  Number of seconds after which the health probe times out. Defaults to 1 second.
  Minimum value is 1.
    """,
    )

  def Run(self, args):
    is_custom_weights_model = args.model.startswith('gs://')
    if not is_custom_weights_model:
      validation.ValidateModelGardenModelArgs(args)
    validation.ValidateDisplayName(args.endpoint_display_name)
    region_ref = args.CONCEPTS.region.Parse()
    args.region = region_ref.AsDict()['locationsId']
    version = constants.BETA_VERSION
    is_hf_model = '@' not in args.model

    region = 'us-central1' if _IsDefaultUniverse() else None
    with endpoint_util.AiplatformEndpointOverrides(version, region=region):
      # Custom weights model deployment.
      if is_custom_weights_model:

        if not (
            bool(args.machine_type)
            == bool(args.accelerator_type)
            == bool(args.accelerator_count)
        ):
          raise c_exceptions.InvalidArgumentException(
              '--machine-type, --accelerator-type and --accelerator-count',
              ' Arguments for MachineType, AcceleratorType and AcceleratorCount'
              ' must either all be provided or all be empty for custom weights'
              ' model deployment.',
          )

        machine_spec = None
        # Check accelerator quota.
        if args.machine_type:
          model_garden_utils.CheckAcceleratorQuota(
              args,
              machine_type=args.machine_type,
              accelerator_type=args.accelerator_type,
              accelerator_count=args.accelerator_count,
          )
          client = apis.GetClientInstance(
              constants.AI_PLATFORM_API_NAME,
              constants.AI_PLATFORM_API_VERSION[version],
          )

          machine_spec = client.MESSAGES_MODULE.GoogleCloudAiplatformV1beta1MachineSpec(
              machineType=args.machine_type,
              acceleratorType=client.MESSAGES_MODULE.GoogleCloudAiplatformV1beta1MachineSpec.AcceleratorTypeValueValuesEnum(
                  args.accelerator_type
              ),
              acceleratorCount=args.accelerator_count,
          )

        # Deploy the model.
        with endpoint_util.AiplatformEndpointOverrides(
            version, region=args.region
        ):
          default_endpoint_name = '-'.join([
              'custom-weights',
              str(time.time()).split('.')[0],
              'mg-cli-deploy',
          ])
          mg_client = client_mg.ModelGardenClient()
          operation_client = operations.OperationsClient(version=version)
          endpoint_name = (
              args.endpoint_display_name
              if args.endpoint_display_name
              else default_endpoint_name
          )

          model_garden_utils.Deploy(
              args,
              machine_spec,
              endpoint_name,
              args.model,
              operation_client,
              mg_client,
          )
      else:
        # Model Garden model deployment.
        # Step 1: Fetch PublisherModel data, including deployment configs. Use
        # us-central1 because all data are stored in us-central1.
        mg_client = client_mg.ModelGardenClient()
        if is_hf_model:
          # Convert to lower case because API only takes in lower case.
          publisher_name, model_name = args.model.lower().split('/')

          try:
            publisher_model = mg_client.GetPublisherModel(
                model_name=f'publishers/{publisher_name}/models/{model_name}',
                is_hugging_face_model=True,
            )
          except apitools_exceptions.HttpNotFoundError:
            raise c_exceptions.UnknownArgumentException(
                '--model',
                f'{args.model} is not a supported Hugging Face'
                ' model for deployment in Model Garden.',
            )

          default_endpoint_name = '-'.join(
              [publisher_name, model_name, 'hf', 'mg-cli-deploy']
          )
          api_model_arg = f'{publisher_name}/{model_name}'
        else:
          # Convert to lower case because API only takes in lower case.
          publisher_name, model_and_version_name = args.model.lower().split('/')

          try:
            publisher_model = mg_client.GetPublisherModel(
                f'publishers/{publisher_name}/models/{model_and_version_name}'
            )
          except apitools_exceptions.HttpNotFoundError:
            raise c_exceptions.UnknownArgumentException(
                '--model',
                f'{args.model} is not a supported Model Garden model for'
                ' deployment in Model Garden.',
            )

          default_endpoint_name = '-'.join([
              publisher_name,
              model_and_version_name.split('@')[1],
              'mg-cli-deploy',
          ])
          api_model_arg = (
              f'publishers/{publisher_name}/models/{model_and_version_name}'
          )

        deploy_config = model_garden_utils.GetDeployConfig(
            args, publisher_model
        )

        # Step 2: Check accelerator quota.
        model_garden_utils.CheckAcceleratorQuota(
            args,
            machine_type=deploy_config.dedicatedResources.machineSpec.machineType,
            accelerator_type=str(
                deploy_config.dedicatedResources.machineSpec.acceleratorType
            ),
            accelerator_count=deploy_config.dedicatedResources.machineSpec.acceleratorCount,
        )
        # Clear the aiplatform URI value so that new values can be set.
        properties.VALUES.api_endpoint_overrides.aiplatform.Set(None)

        # Step 3: Deploy the model.
        with endpoint_util.AiplatformEndpointOverrides(
            version, region=args.region
        ):
          mg_client = client_mg.ModelGardenClient()
          operation_client = operations.OperationsClient(version=version)
          endpoint_name = (
              args.endpoint_display_name
              if args.endpoint_display_name
              else default_endpoint_name
          )

          model_garden_utils.Deploy(
              args,
              deploy_config.dedicatedResources.machineSpec,
              endpoint_name,
              api_model_arg,
              operation_client,
              mg_client,
          )
