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
"""Command to create a catalog template revision."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.design_center import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.design_center import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml

_DETAILED_HELP = {
    'DESCRIPTION': 'Create a new catalog template revision.',
    'EXAMPLES': """ \
        To create a new catalog template revision named `my-revision` for the template `my-template`, within the catalog `my-catalog` and space `my-space`, in location `us-central1` and project `my-project`, using a Developer Connect repository as the source, run:

          $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --description="My test revision description" \\
            --developer-connect-repo=projects/my-project/locations/us-central1/connections/my-connection/gitRepositoryLinks/my-repo \\
            --developer-connect-repo-ref=refs/tags/v1.0.0 \\
            --developer-connect-repo-dir=modules/my-product

          Or run using the full resource name:

            $ {command} projects/my-project/locations/us-central1/spaces/my-space/catalogs/my-catalog/templates/my-template/revisions/my-revision \\
            --description="My test revision description" \\
            --developer-connect-repo=projects/my-project/locations/us-central1/connections/my-connection/gitRepositoryLinks/my-repo \\
            --developer-connect-repo-ref=refs/tags/v1.0.0 \\
            --developer-connect-repo-dir=modules/my-product

          To create a revision using a metadata file from a local path, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --developer-connect-repo=projects/my-project/locations/us-central1/connections/my-connection/gitRepositoryLinks/my-repo \\
            --developer-connect-repo-ref=refs/tags/v1.0.0 \\
            --developer-connect-repo-dir=modules/my-product \\
            --metadata=/path/to/metadata.yaml

          To create a revision using a Git repository as the source, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --git-source-repo=GoogleCloudPlatform/terraform-google-cloud-run \\
            --git-source-ref-tag=v1.0.0 \\
            --git-source-dir=modules/my-product

          To create a revision using a Google Cloud Storage URI as the source, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --gcs-source-uri=gs://my-bucket/my-template

          To create a revision using an OCI repository as the source, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --oci-repo-uri=oci://us-west1-docker.pkg.dev/my-project/my-repo/my-chart \\
            --oci-repo-version=1.0.0

          To create a revision using an Application Template Revision as the source, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --application-template-revision-source=projects/my-project/locations/us-central1/spaces/my-space/applicationTemplates/my-app-template/revisions/a1

          To create a revision using Git source and a metadata file from a local path, run:

            $ {command} my-revision --project=my-project --location=us-central1 \\
            --space=my-space \\
            --catalog=my-catalog \\
            --template=my-template \\
            --git-source-repo=GoogleCloudPlatform/terraform-google-cloud-run \\
            --git-source-ref-tag=v1.0.0 \\
            --git-source-dir=modules/my-product \\
            --metadata=/path/to/metadata.yaml
          """,
    'API REFERENCE': """ \
        This command uses the designcenter/v1alpha API. The full documentation for
        this API can be found at:
        http://cloud.google.com/application-design-center/docs
        """,
}


def _set_git_reference(git_reference_message, ref_string):
  """Populates the correct oneof field in a GitReference message.

  This function parses the reference string to determine if it is a tag,
  branch, or commit. It supports explicit formats (e.g., 'refs/tags/v1.0.0' or
  'refs/heads/modules/my-product' or
  'refs/commits/269b518b99d06b31ff938a2d182e75f5e41941c7').

  Args:
    git_reference_message: The GitReference message to populate.
    ref_string: The user-provided reference string.
  """
  if not ref_string:
    return

  # Check for explicit Git reference formats.
  if ref_string.startswith('refs/tags/'):
    git_reference_message.refTag = ref_string[len('refs/tags/') :]
    return
  if ref_string.startswith('refs/heads/'):
    git_reference_message.branch = ref_string[len('refs/heads/') :]
    return
  if ref_string.startswith('refs/commits/'):
    git_reference_message.commitSha = ref_string[len('refs/commits/') :]
    return

  # If no format matches, raise an error.
  raise exceptions.InvalidArgumentException(
      '--developer-connect-repo-ref',
      'Git reference "{}" does not match the required format: '
      '"refs/tags/<tag>", "refs/heads/<branch>", or "refs/commits/<sha>".'
      .format(ref_string),
  )


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.UniverseCompatible
class Create(base.CreateCommand):
  """Create a new catalog template revision."""

  detailed_help = _DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Register flags for this command."""
    base.ASYNC_FLAG.AddToParser(parser)
    flags.AddCreateCatalogTemplateRevisionFlags(parser)

  def Run(self, args):
    """This is what gets called when the user runs this command."""

    client = utils.GetClientInstance(self.ReleaseTrack())
    messages = utils.GetMessagesModule(self.ReleaseTrack())
    catalog_template_revision = messages.CatalogTemplateRevision()

    revision_ref = args.CONCEPTS.revision.Parse()
    parent = revision_ref.Parent().RelativeName()
    revision_id = revision_ref.Name()

    if (
        args.IsSpecified('git_source_repo')
        or args.IsSpecified('git_source_ref_tag')
        or args.IsSpecified('git_source_dir')
    ):
      catalog_template_revision.gitSource = messages.GitSource(
          repo=args.git_source_repo,
          refTag=args.git_source_ref_tag,
          dir=args.git_source_dir,
      )
    elif (
        args.IsSpecified('developer_connect_repo')
        or args.IsSpecified('developer_connect_repo_ref')
        or args.IsSpecified('developer_connect_repo_dir')
    ):
      git_reference = messages.GitReference()
      # Determine which 'oneof' field to set based on the reference string.
      _set_git_reference(git_reference, args.developer_connect_repo_ref)

      catalog_template_revision.developerConnectSourceConfig = (
          messages.DeveloperConnectSourceConfig(
              developerConnectRepoUri=args.developer_connect_repo,
              reference=git_reference,
              dir=args.developer_connect_repo_dir,
          )
      )
    elif args.application_template_revision_source:
      catalog_template_revision.applicationTemplateRevisionSource = (
          args.application_template_revision_source
      )
    elif args.gcs_source_uri:
      catalog_template_revision.gcsSourceUri = args.gcs_source_uri
    elif args.IsSpecified('oci_repo_uri') or args.IsSpecified(
        'oci_repo_version'
    ):
      catalog_template_revision.ociRepo = messages.OciRepo(
          uri=args.oci_repo_uri,
          version=args.oci_repo_version,
      )

    if args.description:
      catalog_template_revision.description = args.description

    if args.metadata:
      try:
        # The arg type YAMLFileContents() already loads the file.
        metadata_dict = args.metadata
        if 'spec' in metadata_dict:
          catalog_template_revision.metadataInput = messages.MetadataInput(
              spec=metadata_dict['spec']
          )
        else:
          raise exceptions.InvalidArgumentException(
              '--metadata',
              'The metadata file must contain a top-level "spec" key.',
          )
      except yaml.YAMLParseError as e:
        raise exceptions.InvalidArgumentException(
            '--metadata', f'Error parsing YAML file: {e}'
        )

    request = messages.DesigncenterProjectsLocationsSpacesCatalogsTemplatesRevisionsCreateRequest(
        parent=parent,
        catalogTemplateRevisionId=revision_id,
        catalogTemplateRevision=catalog_template_revision,
    )

    operation = (
        client.projects_locations_spaces_catalogs_templates_revisions.Create(
            request
        )
    )
    log.status.Print(
        'Create request issued for: [{0}]'.format(revision_ref.Name())
    )
    if args.async_:
      return operation

    response = utils.WaitForOperation(
        client=client,
        operation=operation,
        message='Waiting for operation [{0}] to complete'.format(
            operation.name
        ),
        max_wait_sec=7200,
    )
    log.status.Print('Created revision [{0}].'.format(revision_ref.Name()))
    return response
