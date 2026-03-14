# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""Upgrade a 1st gen Cloud Function to the Cloud Run function."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import collections

from googlecloudsdk.api_lib.functions import api_enablement
from googlecloudsdk.api_lib.functions.v2 import client as client_v2
from googlecloudsdk.api_lib.functions.v2 import exceptions
from googlecloudsdk.api_lib.functions.v2 import util as api_util
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as calliope_exceptions
from googlecloudsdk.command_lib.eventarc import types as trigger_types
from googlecloudsdk.command_lib.functions import flags
from googlecloudsdk.command_lib.functions import run_util
from googlecloudsdk.command_lib.functions import service_account_util
from googlecloudsdk.command_lib.functions.v2 import deploy_util
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io
import six

SUPPORTED_EVENT_TYPES = (
    'google.pubsub.topic.publish',
    'providers/cloud.pubsub/eventTypes/topic.publish',
)

UpgradeAction = collections.namedtuple(
    'UpgradeAction',
    [
        'target_state',
        'prompt_msg',
        'op_description',
        'success_msg',
    ],
)
_ABORT_GUIDANCE_MSG = (
    'You can abort the upgrade process at any time by rerunning this command'
    ' with the --abort flag.'
)

_SETUP_CONFIG_ACTION = UpgradeAction(
    target_state='SETUP_FUNCTION_UPGRADE_CONFIG_SUCCESSFUL',
    prompt_msg=(
        'This creates a Cloud Run function with the same name [{}], code, and'
        ' configuration as the 1st gen function. The 1st gen function will'
        ' continue to serve traffic until you redirect traffic to the Cloud Run'
        ' function in the next step.\n\nTo learn more about the differences'
        ' between 1st gen and Cloud Run functions, visit:'
        ' https://cloud.google.com/functions/docs/concepts/version-comparison'
    ),
    op_description=(
        'Setting up the upgrade for function. Please wait while we'
        ' duplicate the 1st gen function configuration and code to a Cloud Run'
        ' function.'
    ),
    success_msg=(
        'The Cloud Run function is now ready for testing:\n  {}\nView the'
        ' function upgrade testing guide for steps on how to test the function'
        ' before redirecting traffic to it.\n\nOnce you are ready to redirect'
        ' traffic, rerun this command with the --redirect-traffic flag.'
    )
    + '\n\n'
    + _ABORT_GUIDANCE_MSG,
)

_REDIRECT_TRAFFIC_ACTION = UpgradeAction(
    target_state='REDIRECT_FUNCTION_UPGRADE_TRAFFIC_SUCCESSFUL',
    prompt_msg=(
        'This will redirect all traffic from the 1st gen function [{}] to its'
        ' Cloud Run function copy. Please ensure that you have tested the Cloud'
        ' Run function before proceeding.'
    ),
    op_description='Redirecting traffic to the Cloud Run function.',
    success_msg=(
        'The Cloud Run function is now serving all traffic.'
        ' If you experience issues, rerun this command with the'
        ' --rollback-traffic flag. Otherwise, once you are ready to finalize'
        ' the upgrade, rerun this command with the --commit flag.'
    )
    + '\n\n'
    + _ABORT_GUIDANCE_MSG,
)

_ROLLBACK_TRAFFIC_ACTION = UpgradeAction(
    target_state='SETUP_FUNCTION_UPGRADE_CONFIG_SUCCESSFUL',
    prompt_msg=(
        'This will rollback all traffic from the Cloud Run function copy [{}]'
        ' to the original 1st gen function. The Cloud Run function is still'
        ' available for testing.'
    ),
    op_description='Rolling back traffic to the 1st gen function.',
    success_msg=(
        'The 1st gen function is now serving all traffic. The Cloud Run'
        ' function is still available for testing.'
    )
    + '\n\n'
    + _ABORT_GUIDANCE_MSG,
)

_ABORT_ACTION = UpgradeAction(
    target_state='ELIGIBLE_FOR_2ND_GEN_UPGRADE',
    prompt_msg=(
        'This will abort the upgrade process and delete the Cloud Run function'
        ' copy of the 1st gen function [{}].'
    ),
    op_description='Aborting the upgrade for function.',
    success_msg=(
        'Upgrade aborted and the Cloud Run function was successfully deleted.'
    ),
)

_COMMIT_ACTION = UpgradeAction(
    target_state=None,
    prompt_msg=(
        'This will complete the upgrade process for function [{}] and delete'
        ' the 1st gen copy.\n\nThis action cannot be undone.'
    ),
    op_description=(
        'Completing the upgrade and deleting the 1st gen copy for function.'
    ),
    success_msg=(
        'Upgrade completed and the 1st gen copy was successfully'
        ' deleted.\n\nYour function will continue to be available at the'
        ' following endpoints:\n{}\nReminder, your function can now be managed'
        ' through the Cloud Run API. Any event triggers are now Eventarc'
        ' triggers and can be managed through Eventarc API.'
    ),
)

# Source: http://cs/f:UpgradeStateMachine.java
_VALID_TRANSITION_ACTIONS = {
    'ELIGIBLE_FOR_2ND_GEN_UPGRADE': [_SETUP_CONFIG_ACTION],
    'UPGRADE_OPERATION_IN_PROGRESS': [],
    'SETUP_FUNCTION_UPGRADE_CONFIG_SUCCESSFUL': [
        _REDIRECT_TRAFFIC_ACTION,
        _ABORT_ACTION,
    ],
    'SETUP_FUNCTION_UPGRADE_CONFIG_ERROR': [
        _SETUP_CONFIG_ACTION,
        _ABORT_ACTION,
    ],
    'ABORT_FUNCTION_UPGRADE_ERROR': [_ABORT_ACTION],
    'REDIRECT_FUNCTION_UPGRADE_TRAFFIC_SUCCESSFUL': [
        _COMMIT_ACTION,
        _ROLLBACK_TRAFFIC_ACTION,
        _ABORT_ACTION,
    ],
    'REDIRECT_FUNCTION_UPGRADE_TRAFFIC_ERROR': [
        _REDIRECT_TRAFFIC_ACTION,
        _ABORT_ACTION,
    ],
    'ROLLBACK_FUNCTION_UPGRADE_TRAFFIC_ERROR': [
        _ROLLBACK_TRAFFIC_ACTION,
        _ABORT_ACTION,
    ],
    'COMMIT_FUNCTION_UPGRADE_SUCCESSFUL': [],
    'COMMIT_FUNCTION_UPGRADE_ERROR': [_COMMIT_ACTION],
}  # type: dict[str, list[UpgradeAction]]


def _ValidateStateTransition(upgrade_state, action):
  # type: (_,UpgradeAction) -> None
  """Validates whether the action is a valid action for the given upgrade state."""
  upgrade_state_str = six.text_type(upgrade_state)
  if upgrade_state_str == 'UPGRADE_OPERATION_IN_PROGRESS':
    raise exceptions.FunctionsError(
        'An upgrade operation is already in progress for this function.'
        ' Please try again later.'
    )

  if upgrade_state_str == action.target_state:
    raise exceptions.FunctionsError(
        'This function is already in the desired upgrade state: {}'.format(
            upgrade_state
        )
    )

  if action not in _VALID_TRANSITION_ACTIONS[upgrade_state_str]:
    raise exceptions.FunctionsError(
        'This function is not eligible for this operation. Its current upgrade'
        " state is '{}'.".format(upgrade_state)
    )


# Source: http://cs/f:Gen1UpgradeEligibilityValidator.java
def _RaiseNotEligibleForUpgradeError(function):
  """Raises an error when the function is not eligible for upgrade."""
  if six.text_type(function.environment) == 'GEN_2':
    raise exceptions.FunctionsError(
        f'Function [{function.name}] is not eligible for Upgrade. To migrate to'
        ' Cloud Run function, please detach the function using `gcloud'
        ' functions detach` instead.'
    )
  if ':' in api_util.GetProject():
    raise exceptions.FunctionsError(
        f'Function [{function.name}] is not eligible for Cloud Run function'
        ' upgrade. It is in domain-scoped project that Cloud Run does not'
        ' support.'
    )
  if six.text_type(function.state) != 'ACTIVE':
    raise exceptions.FunctionsError(
        f'Function [{function.name}] is not eligible for Cloud Run function'
        f' upgrade. It is in state [{function.state}].'
    )
  if (
      not function.url
      and function.eventTrigger.eventType not in SUPPORTED_EVENT_TYPES
  ):
    raise exceptions.FunctionsError(
        f'Function [{function.name}] is not eligible for Cloud Run function'
        ' upgrade. Only HTTP functions and Pub/Sub triggered functions are'
        ' supported.'
    )
  raise exceptions.FunctionsError(
      f'Function [{function.name}] is not eligible for Cloud Run function'
      ' upgrade.'
  )


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpgradeBeta(base.Command):
  """Upgrade a 1st gen Cloud Function to the Cloud Run function."""

  detailed_help = {
      'DESCRIPTION': '{description}',
      'EXAMPLES': """\
          To start the upgrade process for a 1st gen function `foo` and create a Cloud Run function copy, run:

            $ {command} foo --setup-config

          Once you are ready to redirect traffic to the Cloud Run function copy, run:

            $ {command} foo --redirect-traffic

          If you find you need to do more local testing you can rollback traffic to the 1st gen copy:

            $ {command} foo --rollback-traffic

          Once you're ready to finish upgrading and delete the 1st gen copy, run:

            $ {command} foo --commit

          You can abort the upgrade process at any time by running:

            $ {command} foo --abort
          """,
  }

  @staticmethod
  def Args(parser):
    flags.AddFunctionResourceArg(parser, 'to upgrade')
    flags.AddUpgradeFlags(parser)

  def Run(self, args):
    client = client_v2.FunctionsClient(self.ReleaseTrack())
    function_ref = args.CONCEPTS.name.Parse()
    function_name = function_ref.RelativeName()

    function = client.GetFunction(function_name)

    if not function:
      raise exceptions.FunctionsError(
          'Function [{}] does not exist.'.format(function_name)
      )

    if not function.upgradeInfo:
      _RaiseNotEligibleForUpgradeError(function)

    upgrade_state = function.upgradeInfo.upgradeState

    if (
        six.text_type(upgrade_state)
        == 'INELIGIBLE_FOR_UPGRADE_UNTIL_REDEPLOYMENT'
    ):
      raise exceptions.FunctionsError(
          f'Function [{function.name}] is not eligible for Cloud Run function'
          f' upgrade. The runtime [{function.buildConfig.runtime}] is not'
          ' supported. Please update to a supported runtime instead and try'
          ' again. Use `gcloud functions runtimes list` to get a list of'
          ' available runtimes.'
      )

    action = None
    action_fn = None
    if args.redirect_traffic:
      action = _REDIRECT_TRAFFIC_ACTION
      action_fn = client.RedirectFunctionUpgradeTraffic
    elif args.rollback_traffic:
      action = _ROLLBACK_TRAFFIC_ACTION
      action_fn = client.RollbackFunctionUpgradeTraffic
    elif args.commit:
      action = _COMMIT_ACTION
      action_fn = client.CommitFunctionUpgrade
    elif args.abort:
      action = _ABORT_ACTION
      action_fn = client.AbortFunctionUpgrade
    elif args.setup_config:
      action = _SETUP_CONFIG_ACTION
      action_fn = client.SetupFunctionUpgradeConfig
    else:
      raise calliope_exceptions.OneOfArgumentsRequiredException(
          [
              '--abort',
              '--commit',
              '--redirect-traffic',
              '--rollback-traffic',
              '--setup-config',
          ],
          'One of the upgrade step must be specified.',
      )

    _ValidateStateTransition(upgrade_state, action)

    message = action.prompt_msg.format(function_name)
    if not console_io.PromptContinue(message, default=True):
      return

    if action == _SETUP_CONFIG_ACTION:
      # Preliminary checks to ensure APIs and permissions are set up in case
      # this is the user's first time deploying a Cloud Run function.
      api_enablement.PromptToEnableApiIfDisabled('cloudbuild.googleapis.com')
      api_enablement.PromptToEnableApiIfDisabled(
          'artifactregistry.googleapis.com'
      )
      trigger = function.eventTrigger
      if not trigger and args.trigger_service_account:
        raise calliope_exceptions.InvalidArgumentException(
            '--trigger-service-account',
            'Trigger service account can only be specified for'
            ' event-triggered functions.',
        )
      if trigger and trigger_types.IsPubsubType(trigger.eventType):
        deploy_util.ensure_pubsub_sa_has_token_creator_role()
      if trigger and trigger_types.IsAuditLogType(trigger.eventType):
        deploy_util.ensure_data_access_logs_are_enabled(trigger.eventFilters)
      operation = action_fn(function_name, args.trigger_service_account)
    else:
      operation = action_fn(function_name)

    description = action.op_description
    api_util.WaitForOperation(
        client.client, client.messages, operation, description
    )

    log.status.Print()

    if action == _SETUP_CONFIG_ACTION:
      function = client.GetFunction(function_name)
      if function.eventTrigger:
        # Checks trigger service account has route.invoker permission on the
        # project. If not, prompts to add the run invoker role to the function.
        service_account_util.ValidateAndBindTriggerServiceAccount(
            function,
            api_util.GetProject(),
            args.trigger_service_account,
            is_gen2=False,
        )
      log.status.Print(
          action.success_msg.format(function.upgradeInfo.serviceConfig.uri)
      )
    elif action == _COMMIT_ACTION:
      service = run_util.GetService(function)
      urls_strings = ''.join(f'* {url}\n' for url in service.urls)
      log.status.Print(action.success_msg.format(urls_strings))
    else:
      log.status.Print(action.success_msg)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpgradeAlpha(UpgradeBeta):
  """Upgrade a 1st gen Cloud Function to the Cloud Run function."""
