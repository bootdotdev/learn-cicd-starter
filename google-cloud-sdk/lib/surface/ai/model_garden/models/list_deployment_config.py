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
"""The command lists the deployment configurations of a given model supported by Model Garden."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from apitools.base.py import exceptions as apitools_exceptions
from googlecloudsdk.api_lib.ai.model_garden import client as client_mg
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as c_exceptions
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util
from googlecloudsdk.command_lib.ai import validation
from googlecloudsdk.core import exceptions as core_exceptions


_DEFAULT_FORMAT = """
        table(
            dedicatedResources.machineSpec.machineType:label=MACHINE_TYPE,
            dedicatedResources.machineSpec.acceleratorType:label=ACCELERATOR_TYPE,
            dedicatedResources.machineSpec.acceleratorCount:label=ACCELERATOR_COUNT,
            containerSpec.imageUri:label=CONTAINER_IMAGE_URI
        )
    """


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class ListDeployMentConfig(base.ListCommand):
  """List the machine specifications supported by and verified for a model in Model Garden.

  ## EXAMPLES

  To list the supported machine specifications for `google/gemma2@gemma-2-9b`,
  run:

    $ gcloud ai model-garden models list-deployment-config
    --model=google/gemma2@gemma-2-9b

  To list the supported machine specifications for a Hugging Face model
  `meta-llama/Meta-Llama-3-8B`, run:

    $ gcloud ai model-garden models list-deployment-config
    --model=meta-llama/Meta-Llama-3-8B
  """

  def _GetMultiDeploy(self, args, version):
    mg_client = client_mg.ModelGardenClient(version)
    # Convert to lower case because API only takes in lower case.
    publisher_name, model_name = args.model.lower().split('/')
    is_hugging_face_model = client_mg.IsHuggingFaceModel(args.model)

    try:
      publisher_model = mg_client.GetPublisherModel(
          model_name=f'publishers/{publisher_name}/models/{model_name}',
          is_hugging_face_model=is_hugging_face_model,
          include_equivalent_model_garden_model_deployment_configs=True,
          hugging_face_token=args.hugging_face_access_token,
      )
      return (
          publisher_model.supportedActions.multiDeployVertex.multiDeployVertex
      )
    except apitools_exceptions.HttpError as e:
      if (
          e.status_code == 400
          and 'No deploy config found for model' in e.content
      ):
        raise c_exceptions.UnknownArgumentException(
            '--model',
            f'{args.model} is not a supported Hugging Face model for deployment'
            ' in Model Garden because there is no deployment config found'
            ' for it.',
        )
      elif e.status_code == 404 and 'Could not get model' in e.content:
        raise c_exceptions.UnknownArgumentException(
            '--model', f'Could not get {args.model} from Hugging Face.'
        )
      elif e.status_code == 404 and 'Publisher Model' in e.content:
        raise c_exceptions.UnknownArgumentException(
            '--model',
            f'{args.model} is not a supported model in Model Garden.',
        )
    except AttributeError:
      raise core_exceptions.Error(
          'Model does not support deployment, please enter a deploy-able model'
          ' instead. You can use the `gcloud alpha/beta ai model-garden models'
          ' list` command to find out which ones are currently supported by the'
          ' `deploy` command.'
      )

  @staticmethod
  def Args(parser):
    # Remove the flags that are not supported by this command.
    base.LIMIT_FLAG.RemoveFromParser(parser)
    base.PAGE_SIZE_FLAG.RemoveFromParser(parser)
    base.URI_FLAG.RemoveFromParser(parser)

    parser.display_info.AddFormat(_DEFAULT_FORMAT)
    base.Argument(
        '--model',
        help=(
            'The model to be deployed. If it is a Model Garden model, it should'
            ' be in the format of'
            ' `{publisher_name}/{model_name}@{model_version_name}, e.g.'
            ' `google/gemma2@gemma-2-2b`. If it is a Hugging Face model, it'
            ' should be in the convention of Hugging Face models, e.g.'
            ' `meta-llama/Meta-Llama-3-8B`.'
        ),
        required=True,
    ).AddToParser(parser)
    base.Argument(
        '--hugging-face-access-token',
        help=(
            'The access token from Hugging Face needed to read the model'
            ' artifacts of gated models in order to generate the deployment'
            ' configs. It is only needed when the Hugging Face model to deploy'
            ' is gated and not verified by Model Garden. You can use the'
            ' `gcloud ai alpha/beta model-garden models list` command to find'
            ' out which ones are verified by Model Garden.'
        ),
    ).AddToParser(parser)

  def Run(self, args):
    validation.ValidateModelGardenModelArgs(args)
    version = constants.BETA_VERSION

    with endpoint_util.AiplatformEndpointOverrides(
        version, region='us-central1'
    ):
      return self._GetMultiDeploy(args, version)
