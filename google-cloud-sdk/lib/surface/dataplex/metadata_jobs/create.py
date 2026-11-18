# -*- coding: utf-8 -*- #
# Copyright 2025 Google Inc. All Rights Reserved.
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
"""`gcloud dataplex metadata-jobs create` command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dataplex import metadata_job as metadata_job_lib
from googlecloudsdk.api_lib.dataplex import util as dataplex_util
from googlecloudsdk.api_lib.util import exceptions as gcloud_exception
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataplex import resource_args
from googlecloudsdk.command_lib.util.apis import arg_utils
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.GA)
class Create(base.Command):
  """Create a Dataplex Metadata Job.

  A metadata job represents a long running job on Dataplex Catalog metadata
  entries. Some operations include importing and exporting metadata into entry
  groups through the usage of entry types and aspect types.

  The Metadata Job ID will be used to identify each configuration run.
  The Metadata Job id must follow these rules:
   * Must contain only lowercase letters, numbers, and hyphens.
   * Must start with a letter.
   * Must end with a number or a letter.
   * Must be between 1-63 characters.
   * Must be unique within the customer project / location.
  """

  detailed_help = {
      'EXAMPLES': """\
          To create a Dataplex Metadata Job with type `IMPORT` and name `my-metadata-job` in location
          `us-central1` with additional parameters, run:

            $ {command} my-metadata-job --location=us-central --project=test-project
            --type=import --import-source-storage-uri=gs://test-storage/
            --import-source-create-time="2019-01-23T12:34:56.123456789Z"
            --import-entry-sync-mode=FULL --import-aspect-sync-mode=INCREMENTAL
            --import-log-level="debug"
            --import-entry-groups=projects/test-project/locations/us-central1/entryGroups/eg1
            --import-entry-types="projects/test-project/locations/us-central1/entryTypes/et1",
                "projects/test-project/locations/us-central1/entryTypes/et2"
            --import-aspect-types="projects/test-project/locations/us-central1/aspectTypes/at1",
                "projects/test-project/locations/us-central1/aspectTypes/at2"

          To create a Dataplex Metadata Job with type `EXPORT` and name `my-metadata-job` in location
          `us-central1` with additional parameters, run:

            $ {command} my-metadata-job --location=us-central --project=test-project
            --type=export --export-output-path=gs://test-storage/
            --export-entry-groups=projects/test-project/locations/us-central1/entryGroups/eg1
            --export-entry-types="projects/test-project/locations/us-central1/entryTypes/et1",
                "projects/test-project/locations/us-central1/entryTypes/et2"
            --export-aspect-types="projects/test-project/locations/us-central1/aspectTypes/at1",
                "projects/test-project/locations/us-central1/aspectTypes/at2"
          """,
  }

  @staticmethod
  def Args(parser):
    resource_args.AddMetadataJobResourceArg(parser, 'to create.')
    parser.add_argument(
        '--type',
        choices={
            'IMPORT': (
                """A Metadata Import Job will ingest, update, or delete entries
                   and aspects into the declared Dataplex entry group."""
            ),
            'EXPORT': (
                """A Metadata Export Job will export entries and aspects from
                   the declared Dataplex scope to the specified Cloud
                   Storage location."""
            ),
        },
        type=arg_utils.ChoiceToEnumName,
        help='Type',
        required=True,
    )
    parser.add_argument(
        '--validate-only',
        action='store_true',
        default=False,
        help="Validate the create action, but don't actually perform it.",
    )
    spec = parser.add_group(
        help='Settings for metadata job operation.', mutex=True, required=True
    )
    import_spec = spec.add_group(
        help='Settings for metadata import job operation.'
    )
    import_scope = import_spec.add_group(
        help=
        """A boundary on the scope of impact that the metadata import job can
        have.""",
        required=True,
    )
    import_scope.add_argument(
        '--import-entry-groups',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_ENTRY_GROUPS',
        help="""The list of entry groups to import metadata jobs into.""",
    )
    import_scope.add_argument(
        '--import-entry-types',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_ENTRY_TYPES',
        help="""The list of entry types to import metadata jobs into.""",
    )
    import_scope.add_argument(
        '--import-aspect-types',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_ASPECT_TYPES',
        help="""The list of aspect types to import metadata jobs into.""",
    )
    import_scope.add_argument(
        '--import-glossaries',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_GLOSSARIES',
        help="""The list of glossaries to import metadata jobs into.""",
    )
    import_scope.add_argument(
        '--import-entry-link-types',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_ENTRY_LINK_TYPES',
        help="""The list of entry link types to import metadata jobs into.""",
    )
    import_scope.add_argument(
        '--import-referenced-entry-scopes',
        type=arg_parsers.ArgList(),
        metavar='IMPORT_REFERENCED_ENTRY_SCOPES',
        help="""The list of referenced entry scopes to import metadata jobs into.""",
    )

    import_spec.add_argument(
        '--import-source-storage-uri',
        help='The Dataplex source storage URI to import metadata from.',
        required=True,
    )
    import_spec.add_argument(
        '--import-source-create-time',
        help=
        """Time at which the event took place. See `$ gcloud topic datetimes`
        for information on supported time formats.""",
    )
    import_spec.add_argument(
        '--import-entry-sync-mode',
        choices={
            'FULL': """All resources in the job's scope are modified. If a
                       resource exists in Dataplex but isn't included in the
                       metadata import file, the resource is deleted when you
                       run the metadata job. Use this mode to perform a full
                       sync of the set of entries in the job scope.""",
            'INCREMENTAL': """Only the entries and aspects that are explicitly
                           included in the metadata import file are modified.
                           Use this mode to modify a subset of resources while
                           leaving unreferenced resources unchanged. """,
        },
        type=arg_utils.ChoiceToEnumName,
        help='Type',
        required=True,
    )
    import_spec.add_argument(
        '--import-aspect-sync-mode',
        choices={
            'FULL': """All resources in the job's scope are modified. If a
                       resource exists in Dataplex but isn't included in the
                       metadata import file, the resource is deleted when you
                       run the metadata job. Use this mode to perform a full
                       sync of the set of entries in the job scope.""",
            'INCREMENTAL': """Only the entries and aspects that are explicitly
                           included in the metadata import file are modified.
                           Use this mode to modify a subset of resources while
                           leaving unreferenced resources unchanged. """,
        },
        type=arg_utils.ChoiceToEnumName,
        help='Type',
        required=True,
    )
    import_spec.add_argument(
        '--import-log-level',
        choices={
            'DEBUG': (
                """Debug-level logging. Captures detailed logs for each import
                item. Use debug-level logging to troubleshoot issues with
                specific import items. For example, use debug-level logging to
                identify resources that are missing from the job scope, entries
                or aspects that don't conform to the associated entry type or
                aspect type, or other misconfigurations with the metadata import file.."""
            ),
            'INFO': """ Info-level logging. Captures logs at the overall job
                    level. Includes aggregate logs about import items, but
                    doesn't specify which import item has an error..""",
        },
        type=arg_utils.ChoiceToEnumName,
        help='Type',
    )
    export_spec = spec.add_group(
        help='Settings for metadata export job operation.'
    )
    export_spec.add_argument(
        '--export-output-path',
        help='The Cloud Storage location to export metadata to.',
        metavar='EXPORT_OUTPUT_PATH',
        required=True,
    )
    export_scope = export_spec.add_group(
        help="""A boundary on the scope of impact that the metadata export job can
        have.""",
        required=True,
    )
    export_scope_resources = export_scope.add_group(
        mutex=True,
        required=True,
        help="""The scope of resources to export metadata from.""",
    )
    export_scope_resources.add_argument(
        '--export-organization-level',
        type=bool,
        metavar='EXPORT_ORGANIZATION_LEVEL',
        help="""Whether to export metadata at the organization level.""",
    )
    export_scope_resources.add_argument(
        '--export-projects',
        type=arg_parsers.ArgList(),
        metavar='EXPORT_PROJECTS',
        help="""The list of projects to export metadata from.""",
    )
    export_scope_resources.add_argument(
        '--export-entry-groups',
        type=arg_parsers.ArgList(),
        metavar='EXPORT_ENTRY_GROUPS',
        help="""The list of entry groups to export metadata from.""",
    )

    export_scope.add_argument(
        '--export-entry-types',
        type=arg_parsers.ArgList(),
        metavar='EXPORT_ENTRY_TYPES',
        help="""The list of entry types to export metadata from.""",
    )
    export_scope.add_argument(
        '--export-aspect-types',
        type=arg_parsers.ArgList(),
        metavar='EXPORT_ASPECT_TYPES',
        help="""The list of aspect types to export metadata from.""",
    )
    base.ASYNC_FLAG.AddToParser(parser)
    labels_util.AddCreateLabelsFlags(parser)

  @gcloud_exception.CatchHTTPErrorRaiseHTTPException(
      'Status code: {status_code}. {status_message}.'
  )
  def Run(self, args):
    metadata_job = args.CONCEPTS.metadata_job.Parse()
    metadata_job_id = self._GetMetatadataJobId(metadata_job)

    dataplex_client = dataplex_util.GetClientInstance()
    message = dataplex_util.GetMessageModule()
    create_req_op = dataplex_client.projects_locations_metadataJobs.Create(
        message.DataplexProjectsLocationsMetadataJobsCreateRequest(
            metadataJobId=metadata_job_id,
            parent=metadata_job.Parent().RelativeName(),
            googleCloudDataplexV1MetadataJob=metadata_job_lib.GenerateMetadataJob(
                args
            ),
        ),
    )
    validate_only = getattr(args, 'validate_only', False)
    if validate_only:
      log.status.Print('Validation complete.')
      return

    async_ = getattr(args, 'async_', False)
    if not async_:
      metadata_job_lib.WaitForOperation(create_req_op)
      log.CreatedResource(
          metadata_job_id,
          details='Metadata Job created in [{0}]'.format(
              metadata_job.Parent().RelativeName()
          ),
      )
      return

    log.status.Print(
        'Creating [{0}] with operation [{1}].'.format(
            metadata_job_id, create_req_op.name
        )
    )

  def _GetMetatadataJobId(self, metadata_job):
    metadata_job_id = metadata_job.RelativeName().split('/')[-1]

    # The case that the positional JOB ID is not specified.
    if metadata_job_id == resource_args.GENERATE_ID:
      metadata_job_id = None

    return metadata_job_id
