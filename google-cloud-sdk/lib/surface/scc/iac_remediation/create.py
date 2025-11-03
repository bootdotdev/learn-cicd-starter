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
"""Command for remediating a Cloud Security Command Center Finding."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
from typing import Any

from googlecloudsdk.api_lib.scc.iac_remediation import findings
from googlecloudsdk.api_lib.scc.iac_remediation import git
from googlecloudsdk.api_lib.scc.iac_remediation import llm
from googlecloudsdk.api_lib.scc.iac_remediation import prompt
from googlecloudsdk.api_lib.scc.iac_remediation import pull_requests
from googlecloudsdk.api_lib.scc.iac_remediation import terraform
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.scc.iac_remediation import errors
from googlecloudsdk.command_lib.scc.iac_remediation import flags
from googlecloudsdk.core import log


@base.Hidden
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
@base.UniverseCompatible
class Create(base.CreateCommand):
  """Remediates a Security Command Center finding."""

  detailed_help = {
      "DESCRIPTION": "Remediates a Security Command Center finding.",
      "EXAMPLES": """
          Sample usage:

          $ {{command}} scc iac-remediation create --finding-org-id=123456789
          --finding-name=projects/123456789/sources/123456789/locations/global/findings/123456789
          --tfstate-file-paths=/path/to/file1.tfstate,/path/to/file2.tfstate --project-id=my-proj
          --git-config-path=/path/to/config.yaml""",
  }

  @staticmethod
  def Args(parser):
    flags.FINDING_ORG_ID_FLAG.AddToParser(parser)
    flags.FINDING_NAME_FLAG.AddToParser(parser)
    flags.LLM_PROJ_ID_FLAG.AddToParser(parser)
    flags.TFSTATE_FILE_PATHS_LIST_FLAG.AddToParser(parser)
    flags.GIT_CONFIG_FILE_PATH_FLAG.AddToParser(parser)

  def Run(self, args: Any) -> None:
    """Remediates a Security Command Center finding.

    Args:
      args: Arguments for the command.
    """
    git_flag, repo_root_dir = git.is_git_repo()
    if not git_flag:  # Throw error if command is invoked from a non-git repo
      raise errors.GitRepoNotFoundError()
    git.validate_git_config(args.git_config_path)
    git_config_data = args.git_config_path
    log.Print(git_config_data)
    log.Print("repo_root_dir: ", repo_root_dir)
    resp = findings.MakeApiCall(args.finding_org_id, args.finding_name)
    json_resp = json.loads(resp)
    iam_bindings = findings.FetchIAMBinding(json_resp)
    resource_name = findings.FetchResourceName(json_resp)
    tfstate_json_list = terraform.fetch_tfstate_list(
        args.tfstate_file_paths, repo_root_dir
    )
    if not tfstate_json_list:
      log.Print("No TFState files found.")
      return
    tfstate_information = terraform.get_tfstate_information_per_member(
        iam_bindings, tfstate_json_list, resource_name
    )
    if not tfstate_information:
      for tfstate_json in tfstate_json_list:
        if "google_project_iam_policy" in tfstate_json:
          tfstate_information = "google_project_iam_policy"
    tf_files = terraform.find_tf_files(repo_root_dir)
    original_files_content = terraform.read_original_files_content(tf_files)
    for member, role_data in iam_bindings.items():
      tfstate_data = ""
      if tfstate_information and member in tfstate_information:
        tfstate_data = tfstate_information[member]
      input_prompt = prompt.fetch_input_prompt(
          tfstate_data,
          role_data,
          resource_name,
          tf_files,
          member,
      )
      response = llm.MakeLLMCall(input_prompt, args.project_id)
      response_dict = prompt.llm_response_parser(response)
      check, response = terraform.validate_tf_files(response_dict)
      if not check:
        terraform.update_tf_files(original_files_content)
        raise errors.InvalidLLMResponseError(response)
      else:
        log.Print(response)
        git.push_commit(
            response_dict,
            pull_requests.CreateCommitMessage(resp, member),
            git_config_data["remote"],
            git_config_data["branch-prefix"]
            + findings.ParseName(args.finding_name),
        )
        terraform.update_tf_files(response_dict)
    git.raise_pr(
        pull_requests.CreatePRMessage(resp),
        pull_requests.CreatePRMessage(resp),
        git_config_data["remote"],
        git_config_data["branch-prefix"]
        + findings.ParseName(args.finding_name),
        git_config_data["main-branch-name"],
    )
    terraform.update_tf_files(original_files_content)
