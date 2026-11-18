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
"""Command for semi-automatic remediation of SCC findings."""

import copy
import uuid

from googlecloudsdk.api_lib.scc.remediation_intents import const
from googlecloudsdk.api_lib.scc.remediation_intents import converters
from googlecloudsdk.api_lib.scc.remediation_intents import extended_service
from googlecloudsdk.api_lib.scc.remediation_intents import git
from googlecloudsdk.api_lib.scc.remediation_intents import sps_api
from googlecloudsdk.api_lib.scc.remediation_intents import terraform
from googlecloudsdk.api_lib.scc.remediation_intents import validators
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.remediation_intents import flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible


class AutoRemediate(base.SilentCommand, base.CacheCommand):
  """Command for semi-automatic remediation of SCC findings."""
  detailed_help = {
      "DESCRIPTION": """
        Orchestrates the semi-automatic remediation process for SCC findings
        by calling the Remediation Intent APIs.
        """,

      "EXAMPLES": """
          Sample usage:
          Remediate a SCC finding for the organization 1234567890, in the
          terraform repository located at ./terraform-repo.
          $ {{command}} scc remediation-intents auto-remediate \\
            --org-id=1234567890 \\
            --root-dir-path=./terraform-repo \\
            --git-config-path=./git-config.yaml""",
  }

  @staticmethod
  def Args(parser):
    flags.ROOT_DIR_PATH_FLAG.AddToParser(parser)
    flags.ROOT_DIR_PATH_FLAG.SetDefault(parser, ".")
    flags.ORG_ID_FLAG.AddToParser(parser)
    flags.GIT_CONFIG_FILE_PATH_FLAG.AddToParser(parser)

  def Run(self, args) -> None:
    """The main function which is called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.
    """
    # Set up the variables.
    org_id = args.org_id
    git_config_data = args.git_config_path
    root_dir_path = args.root_dir_path
    # The extended service client to interact with the SPS service.
    client = extended_service.ExtendedSPSClient(org_id, base.ReleaseTrack.ALPHA)
    # The converter instance to handle conversion between different data types.
    converter = converters.RemediationIntentConverter(base.ReleaseTrack.ALPHA)
    messages = sps_api.GetMessagesModule(base.ReleaseTrack.ALPHA)

    # Validate the input arguments.
    validators.validate_git_config(git_config_data)
    validators.validate_relative_dir_path(root_dir_path)
    # Create a SCC finding Remediation Intent.

    # Fetch an enqueued remediation intent which needs to be remediated.
    intent_data = client.fetch_enqueued_remediation_intent()
    if (  # Create a new intent if no enqueued intent is found.
        intent_data is None
    ):
      client.create_semi_autonomous_remediation_intent()
      intent_data = client.fetch_enqueued_remediation_intent()
      if intent_data is None:
        # Exit gracefully if still no intent is found.
        log.Print("No remediation intent found to be remediated, exitting...")
        return
    intent_name = intent_data.name

    tf_files = terraform.fetch_tf_files(root_dir_path)
    if not tf_files:  # Exit gracefully if no TF files are found.
      log.Print("No TF files found, exitting...")
      return
    # Parse the TFState file for the given finding data.
    tfstate_data = terraform.parse_tf_file(
        root_dir_path, intent_data.findingData
    )

    log.Print("Remediation started....")
    # Update the state to REMEDIATION_IN_PROGRESS and start the remediation.
    intent_updated = copy.deepcopy(intent_data)
    intent_updated.state = (  # Mark the state as REMEDIATION_IN_PROGRESS.
        messages.RemediationIntent.StateValueValuesEnum.REMEDIATION_IN_PROGRESS
    )
    intent_updated.remediationInput = messages.RemediationInput(
        tfData=messages.TfData(
            fileData=converter.DictFilesToMessage(tf_files),
            tfStateInfo=tfstate_data,
        )
    )
    update_mask = "state,remediation_input"
    intent_updated = client.update_remediation_intent(  # Call the Update API.
        intent_name, update_mask, intent_updated
    )
    if (
        intent_updated.state
        == messages.RemediationIntent.StateValueValuesEnum.REMEDIATION_FAILED
    ):
      log.Print("Remediation failed, exitting...")
      return

    # Retry the remediation process for certain number of times.
    is_remediated = False
    retry_count = 0
    while not is_remediated and retry_count < const.REMEDIATION_RETRY_COUNT:
      log.Print("Remediation retry count: ", retry_count)
      updated_tf_files = converter.MessageFilesToDict(
          intent_updated.remediatedOutput.outputData[0].tfData.fileData
      )
      error_msg = terraform.validate_tf_files(updated_tf_files)
      if error_msg is None:  # Remediation is successful.
        is_remediated = True
        break
      # Send the error details to the server and retry the remediation.
      intent_updated.remediationInput.errorDetails = messages.ErrorDetails(
          reason=error_msg
      )
      update_mask = "remediation_input.error_details"
      intent_updated = client.update_remediation_intent(
          intent_name, update_mask, intent_updated
      )
      if (
          intent_updated.state
          == messages.RemediationIntent.StateValueValuesEnum.REMEDIATION_FAILED
      ):
        log.Print("Remediation failed, exitting...")
        return
      retry_count += 1  # Upate the retry count.
      log.Print("Remediation failed, retrying...")

    if not is_remediated:   # Mark the state as REMEDIATION_FAILED and exit.
      log.Print("Remediation failed: Max retry limit reached.")
      intent_updated.state = (
          messages.RemediationIntent.StateValueValuesEnum.REMEDIATION_FAILED
      )
      update_mask = "state"
      _ = client.update_remediation_intent(  # Call the Update API.
          intent_name, update_mask, intent_updated
      )
      return

    log.Print("Remediation completed successfully.")
    intent_updated.state = (  # Mark the state as REMEDIATION_SUCCESS.
        messages.RemediationIntent.StateValueValuesEnum.REMEDIATION_SUCCESS
    )
    intent_updated.remediationInput.errorDetails = None
    update_mask = "state,remediation_input.error_details"
    intent_updated = client.update_remediation_intent(  # Call the Update API.
        intent_name, update_mask, intent_updated
    )

    # Generate the PR for the remediated output.
    log.Print("Starting PR generation process...")
    updated_tf_files = converter.MessageFilesToDict(
        intent_updated.remediatedOutput.outputData[0].tfData.fileData
    )
    git_config_data["branch-prefix"] += str(uuid.uuid4())

    git.push_commit(
        updated_tf_files,
        const.COMMIT_MSG.format(
            project_id=intent_updated.findingData.findingName.split("/")[1],
            finding_id=intent_updated.findingData.findingName.split("/")[-1],
            category=intent_updated.findingData.category,
        ),
        git_config_data["remote"],
        git_config_data["branch-prefix"],
    )
    log.Print("Commit pushed successfully.")
    # Add the remediation explanation to the PR description.
    pr_status, pr_msg = git.create_pr(
        const.PR_TITLE.format(
            project_id=intent_updated.findingData.findingName.split("/")[1],
            finding_id=intent_updated.findingData.findingName.split("/")[-1],
            category=intent_updated.findingData.category,
        ),
        const.PR_DESC.format(
            remediation_explanation=intent_updated.remediatedOutput.remediationExplanation.replace(
                "`", r"\`"
            ),
            file_modifiers="\n".join(
                f"{fp}: {ea}"
                for fp, ea in (git.get_file_modifiers(updated_tf_files)).items()
            ),
            file_owners="\n".join(
                f"{fp}: {ea}"
                for fp, ea in (
                    git.get_file_modifiers(updated_tf_files, first=True)
                ).items()
            ),
        ),
        git_config_data["remote"],
        git_config_data["branch-prefix"],
        git_config_data["main-branch-name"],
        git_config_data["reviewers"],
    )
    # Update the state and error details if the PR creation fails, and exit.
    if not pr_status:
      log.Print("PR creation failed, exitting...")
      intent_updated.state = (
          messages.RemediationIntent.StateValueValuesEnum.PR_GENERATION_FAILED
      )
      intent_updated.errorDetails = messages.ErrorDetails(reason=pr_msg)
      update_mask = "state,error_details"
      _ = client.update_remediation_intent(
          intent_name, update_mask, intent_updated
      )
      return

    # Finally Update the state and PR details if the PR creation is successful.
    log.Print("PR created successfully.")
    intent_updated.state = (
        messages.RemediationIntent.StateValueValuesEnum.PR_GENERATION_SUCCESS
    )
    intent_updated.remediationArtifacts = messages.RemediationArtifacts(
        prData=messages.PullRequest(
            url=pr_msg,
            modifiedFileOwners=list(
                (git.get_file_modifiers(updated_tf_files, first=True)).values()
            ),
            modifiedFilePaths=list(
                (git.get_file_modifiers(updated_tf_files, first=True)).keys()
            ),
        )
    )
    update_mask = "state,remediation_artifacts"
    _ = client.update_remediation_intent(
        intent_name, update_mask, intent_updated
    )
