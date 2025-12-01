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
"""Command for updating env vars and other configuration info."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from googlecloudsdk.api_lib.run import global_methods
from googlecloudsdk.api_lib.run import worker_pool
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.api_lib.util import messages as messages_util
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.projects import util as projects_util
from googlecloudsdk.command_lib.run import config_changes
from googlecloudsdk.command_lib.run import connection_context
from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.run import flags
from googlecloudsdk.command_lib.run import messages_util as run_messages_util
from googlecloudsdk.command_lib.run import pretty_print
from googlecloudsdk.command_lib.run import serverless_operations
from googlecloudsdk.command_lib.run import stages
from googlecloudsdk.core import config
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources
from googlecloudsdk.core.console import progress_tracker


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
class Replace(base.Command):
  """Create or replace a worker-pool from a YAML worker-pool specification."""

  detailed_help = {
      'DESCRIPTION': """\
          Creates or replaces a worker-pool from a YAML worker-pool specification.
          """,
      'EXAMPLES': """\
          To replace the specification for a worker-pool defined in my-worker-pool.yaml

              $ {command} my-worker-pool.yaml

         """,
  }

  @classmethod
  def CommonArgs(cls, parser):
    # Flags not specific to any platform
    flags.AddAsyncFlag(parser)
    flags.AddClientNameAndVersionFlags(parser)
    flags.AddDryRunFlag(parser)
    parser.add_argument(
        'FILE',
        action='store',
        type=arg_parsers.YAMLFileContents(),
        help=(
            'The absolute path to the YAML file with a Cloud Run worker-pool '
            'definition for the worker-pool to update or create.'
        ),
    )

    # No output by default, can be overridden by --format
    parser.display_info.AddFormat('none')

  @classmethod
  def Args(cls, parser):
    cls.CommonArgs(parser)

  def _ConnectionContext(self, args, region_label):
    return connection_context.GetConnectionContext(
        args, flags.Product.RUN, self.ReleaseTrack(), region_label=region_label
    )

  def _GetBaseChanges(
      self, new_worker_pool, args
  ):  # used by child - pylint: disable=unused-argument
    is_either_specified = args.IsSpecified('client_name') or args.IsSpecified(
        'client_version'
    )
    return [
        config_changes.ReplaceWorkerPoolChange(new_worker_pool),
        config_changes.SetLaunchStageAnnotationChange(self.ReleaseTrack()),
        config_changes.SetClientNameAndVersionAnnotationChange(
            args.client_name if is_either_specified else 'gcloud',
            args.client_version
            if is_either_specified
            else config.CLOUD_SDK_VERSION,
            set_on_template=True,
        ),
    ]

  def _PrintSuccessMessage(self, worker_pool_obj, dry_run, args):
    if args.async_:
      pretty_print.Success(
          'New configuration for [{{bold}}{worker_pool}{{reset}}] is being'
          ' applied asynchronously.'.format(worker_pool=worker_pool_obj.name)
      )
    elif dry_run:
      pretty_print.Success(
          'New configuration has been validated for worker pool '
          '[{{bold}}{worker_pool}{{reset}}].'.format(
              worker_pool=worker_pool_obj.name
          )
      )
    else:
      pretty_print.Success(
          'New configuration has been applied to worker pool '
          '[{{bold}}{worker_pool}{{reset}}].'.format(
              worker_pool=worker_pool_obj.name
          )
      )

  def Run(self, args):
    """Create or Update service from YAML."""
    run_messages = apis.GetMessagesModule(
        global_methods.SERVERLESS_API_NAME,
        global_methods.SERVERLESS_API_VERSION,
    )
    worker_pool_dict = dict(args.FILE)
    # Clear the status field since it is ignored by Cloud Run APIs and can cause
    # issues trying to convert to a message.
    if 'status' in worker_pool_dict:
      del worker_pool_dict['status']
    if (
        'spec' not in worker_pool_dict
        or 'template' not in worker_pool_dict['spec']
    ):
      raise exceptions.ConfigurationError(
          'spec.template is required but missing. '
          'Please check the content in your yaml file.'
      )
    # If spec.template.metadata is not set, add an empty one so that client
    # annotations can be added.
    if 'metadata' not in worker_pool_dict['spec']['template']:
      worker_pool_dict['spec']['template']['metadata'] = {}

    # For cases where YAML contains the project number as metadata.namespace,
    # preemptively convert them to a string to avoid validation failures.
    namespace = worker_pool_dict.get('metadata', {}).get('namespace', None)
    if namespace is not None and not isinstance(namespace, str):
      worker_pool_dict['metadata']['namespace'] = str(namespace)

    new_worker_pool = None  # this avoids a lot of errors.
    try:
      raw_worker_pool = messages_util.DictToMessageWithErrorCheck(
          worker_pool_dict, run_messages.WorkerPool
      )
      new_worker_pool = worker_pool.WorkerPool(raw_worker_pool, run_messages)
    except messages_util.ScalarTypeMismatchError as e:
      exceptions.MaybeRaiseCustomFieldMismatch(
          e,
          help_text=(
              'Please make sure that the YAML file matches the Cloud Run '
              'worker pool definition spec in'
              ' https://cloud.google.com/run/docs/reference/rest/v1/namespaces.workerpools#WorkerPool'
          ),
      )

    # Namespace must match project (or will default to project if not
    # specified).
    namespace = properties.VALUES.core.project.Get()
    if new_worker_pool.metadata.namespace is not None:
      project = namespace
      project_number = projects_util.GetProjectNumber(namespace)
      namespace = new_worker_pool.metadata.namespace
      if namespace != project and namespace != str(project_number):
        raise exceptions.ConfigurationError(
            'Namespace must be project ID [{}] or quoted number [{}] for '
            'Cloud Run (fully managed).'.format(project, project_number)
        )
    new_worker_pool.metadata.namespace = namespace

    changes = self._GetBaseChanges(new_worker_pool, args)
    worker_pool_ref = resources.REGISTRY.Parse(
        new_worker_pool.metadata.name,
        params={
            'namespacesId': new_worker_pool.metadata.namespace,
        },
        collection='run.namespaces.workerpools',
    )

    region_label = (
        new_worker_pool.region if new_worker_pool.is_managed else None
    )

    conn_context = self._ConnectionContext(args, region_label)
    dry_run = args.dry_run if hasattr(args, 'dry_run') else False

    action = (
        'Validating new configuration for'
        if dry_run
        else 'Applying new configuration to'
    )

    with serverless_operations.Connect(conn_context) as client:
      worker_pool_obj = client.GetWorkerPool(worker_pool_ref)

      pretty_print.Info(
          run_messages_util.GetStartDeployMessage(
              conn_context,
              worker_pool_ref,
              operation=action,
              resource_kind_lower='workerpool',
          )
      )

      deployment_stages = stages.WorkerPoolStages()
      header = (
          'Deploying...' if worker_pool_obj else 'Deploying new worker pool...'
      )
      if dry_run:
        header = 'Validating...'
      with progress_tracker.StagedProgressTracker(
          header,
          deployment_stages,
          failure_message='Deployment failed',
          suppress_output=args.async_ or dry_run,
      ) as tracker:
        worker_pool_obj = client.ReplaceWorkerPool(
            worker_pool_ref,
            changes,
            tracker,
            asyn=args.async_,
            dry_run=dry_run,
        )
      self._PrintSuccessMessage(worker_pool_obj, dry_run, args)
      return worker_pool_obj
