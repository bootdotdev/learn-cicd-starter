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
"""The command lists the models in Model Garden and their supported functionalities."""


from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.ai.model_garden import client as client_mg
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.ai import constants
from googlecloudsdk.command_lib.ai import endpoint_util

_SHORT_NAME_FORMAT = (
    'format("{0:s}@{1:s}/{2:s}", name, versionId,'
    ' name.regex("publishers/hf-.*", "@hf", "@mg")).sub("publishers/hf-",'
    ' "").sub("publishers/", "").sub("models/", "").sub("@001/@hf", "").'
    ' sub("/@mg", ""):sort=1'
)
_FULL_RESOURCE_NAME_FORMAT = 'format("{0:s}@{1:s}", name, versionId):sort=1'
_MODEL_ID_LABEL = ':label=MODEL_ID'

_CAN_DEPLOY_FILTER = 'supportedActions.multiDeployVertex.yesno(yes=Yes)'
_CAN_DEPLOY_LABEL = ':label=CAN_DEPLOY'

_CAN_PREDICT_FILTER = 'publisherModelTemplate.yesno(yes=Yes)'
_CAN_PREDICT_LABEL = ':label=CAN_PREDICT'

_DEFAULT_TABLE_FORMAT = (
    f'table({_SHORT_NAME_FORMAT}{_MODEL_ID_LABEL},'
    f' {_CAN_DEPLOY_FILTER}{_CAN_DEPLOY_LABEL},'
    f' {_CAN_PREDICT_FILTER}{_CAN_PREDICT_LABEL})'
)
_SHORT_MODEL_NAME_ONLY_TABLE_FORMAT = (
    f'table({_SHORT_NAME_FORMAT}{_MODEL_ID_LABEL})'
)
_FULL_RESOURCE_NAME_ONLY_TABLE_FORMAT = (
    f'table({_FULL_RESOURCE_NAME_FORMAT}{_MODEL_ID_LABEL})'
)
_FULL_RESOURCE_NAME_TABLE_FORMAT = (
    f'table({_FULL_RESOURCE_NAME_FORMAT}{_MODEL_ID_LABEL},'
    f' {_CAN_DEPLOY_FILTER}{_CAN_DEPLOY_LABEL},'
    f' {_CAN_PREDICT_FILTER}{_CAN_PREDICT_LABEL})'
)


@base.ReleaseTracks(
    base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA, base.ReleaseTrack.GA
)
@base.DefaultUniverseOnly
class List(base.ListCommand):
  """List the publisher models in Model Garden.

  This command lists either all models in Model Garden or all Hugging
  Face models supported by Model Garden.

  Note: Since the number of Hugging Face models is large, the default limit is
  set to 500 with a page size of 100 when listing supported Hugging Face models.
  To override the limit or page size, specify the --limit or --page-size flags,
  respectively. To list all models in Model Garden, use `--limit=unlimited`.
  """

  @staticmethod
  def Args(parser):
    parser.display_info.AddFormat(_DEFAULT_TABLE_FORMAT)
    parser.add_argument(
        '--can-deploy-hugging-face-models',
        action='store_true',
        default=False,
        required=False,
        help='Whether to only list Hugging Face models that can be deployed.',
    )
    parser.add_argument(
        '--model-filter',
        action='store',
        default=None,
        required=False,
        help=(
            'Filter to apply to the model names or the display names of the'
            ' list of models.'
        ),
    )
    parser.add_argument(
        '--full-resource-name',
        action='store_true',
        default=False,
        required=False,
        help='Whether to return the full resource name of the model.',
    )
    base.URI_FLAG.RemoveFromParser(parser)
    base.LIMIT_FLAG.SetDefault(parser, 1000)

  def Run(self, args):
    version = constants.BETA_VERSION

    if args.full_resource_name:
      args.GetDisplayInfo().AddFormat(_FULL_RESOURCE_NAME_TABLE_FORMAT)

    # Set the default page size to 100 if the user requests to list supported
    # Hugging Face models, since there are tens of thousands of Hugging Face
    # models and the call will take a long time.
    if args.can_deploy_hugging_face_models:
      args.GetDisplayInfo().AddFormat(
          _FULL_RESOURCE_NAME_ONLY_TABLE_FORMAT
          if args.full_resource_name
          else _SHORT_MODEL_NAME_ONLY_TABLE_FORMAT
      )
      if args.page_size is None:
        args.page_size = 100

    with endpoint_util.AiplatformEndpointOverrides(
        version, region='us-central1'
    ):
      mg_client = client_mg.ModelGardenClient(version)
      return mg_client.ListPublisherModels(
          limit=args.limit,
          batch_size=args.page_size,
          list_hf_models=args.can_deploy_hugging_face_models,
          model_filter=args.model_filter,
      )
