# -*- coding: utf-8 -*- #
# Copyright 2015 Google LLC. All Rights Reserved.
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

"""Update cluster command."""

from googlecloudsdk.api_lib.dataproc import constants as dataproc_constants
from googlecloudsdk.api_lib.dataproc import dataproc as dp
from googlecloudsdk.api_lib.dataproc import exceptions
from googlecloudsdk.api_lib.dataproc import util
from googlecloudsdk.calliope import actions
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dataproc import clusters
from googlecloudsdk.command_lib.dataproc import flags
from googlecloudsdk.command_lib.dataproc.utils import user_sa_mapping_util
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log
from googlecloudsdk.core.util import times
import six


@base.UniverseCompatible
class Update(base.UpdateCommand):
  """Update labels and/or the number of worker nodes in a cluster.

  Update the number of worker nodes and/or the labels in a cluster.

  ## EXAMPLES

  To resize a cluster, run:

    $ {command} my-cluster --region=us-central1 --num-workers=5

  To change the number preemptible workers in a cluster, run:

    $ {command} my-cluster --region=us-central1 --num-preemptible-workers=5

  To add the label 'customer=acme' to a cluster, run:

    $ {command} my-cluster --region=us-central1 --update-labels=customer=acme

  To update the label 'customer=ackme' to 'customer=acme', run:

    $ {command} my-cluster --region=us-central1 --update-labels=customer=acme

  To remove the label whose key is 'customer', run:

    $ {command} my-cluster --region=us-central1 --remove-labels=customer

  """

  @classmethod
  def Args(cls, parser):
    dataproc = dp.Dataproc(cls.ReleaseTrack())
    base.ASYNC_FLAG.AddToParser(parser)
    # Allow the user to specify new labels as well as update/remove existing
    labels_util.AddUpdateLabelsFlags(parser)
    # Graceful decomissioning timeouts can be up to 24 hours + add 1 hour for
    # deleting VMs, etc.
    flags.AddTimeoutFlag(parser, default='25h')
    flags.AddClusterResourceArg(parser, 'update', dataproc.api_version)
    parser.add_argument(
        '--num-workers',
        type=int,
        help='The new number of worker nodes in the cluster.')
    num_secondary_workers = parser.add_argument_group(mutex=True)
    num_secondary_workers.add_argument(
        '--num-preemptible-workers',
        action=actions.DeprecationAction(
            '--num-preemptible-workers',
            warn=('The `--num-preemptible-workers` flag is deprecated. '
                  'Use the `--num-secondary-workers` flag instead.')),
        type=int,
        hidden=True,
        help='The new number of preemptible worker nodes in the cluster.')
    num_secondary_workers.add_argument(
        '--num-secondary-workers',
        type=int,
        help='The new number of secondary worker nodes in the cluster.')

    parser.add_argument(
        '--graceful-decommission-timeout',
        type=arg_parsers.Duration(lower_bound='0s', upper_bound='1d'),
        help="""
              The graceful decommission timeout for decommissioning Node Managers
              in the cluster, used when removing nodes. Graceful decommissioning
              allows removing nodes from the cluster without interrupting jobs in
              progress. Timeout specifies how long to wait for jobs in progress to
              finish before forcefully removing nodes (and potentially
              interrupting jobs). Timeout defaults to 0 if not set (for forceful
              decommission), and the maximum allowed timeout is 1 day.
              See $ gcloud topic datetimes for information on duration formats.
              """,
    )

    parser.add_argument(
        '--min-secondary-worker-fraction',
        help=(
            'Minimum fraction of new secondary worker nodes added in a scale up'
            ' update operation, required to update the cluster. If it is not'
            ' met, cluster updation will rollback the addition of secondary'
            ' workers. Must be a decimal value between 0 and 1. Defaults to'
            ' 0.0001.'
        ),
        type=float,
    )

    _AddAlphaArguments(parser, cls.ReleaseTrack())

    idle_delete_group = parser.add_mutually_exclusive_group()
    idle_delete_group.add_argument(
        '--max-idle',
        type=arg_parsers.Duration(),
        hidden=True,
        help="""\
        The duration after the last job completes to auto-delete the cluster,
        such as "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    idle_delete_group.add_argument(
        '--no-max-idle',
        action='store_true',
        hidden=True,
        help="""\
        Cancels the cluster auto-deletion by cluster idle duration (configured
         by --max-idle flag)
        """,
    )
    idle_delete_group.add_argument(
        '--delete-max-idle',
        type=arg_parsers.Duration(),
        help="""\
        The duration after the last job completes to auto-delete the cluster,
        such as "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    idle_delete_group.add_argument(
        '--no-delete-max-idle',
        action='store_true',
        help="""\
        Cancels the cluster auto-deletion by cluster idle duration (configured
        by --delete-max-idle flag)
        """)

    auto_delete_group = parser.add_mutually_exclusive_group()
    auto_delete_group.add_argument(
        '--max-age',
        type=arg_parsers.Duration(),
        hidden=True,
        help="""\
        The lifespan of the cluster, with auto-deletion upon completion,
        "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    auto_delete_group.add_argument(
        '--expiration-time',
        type=arg_parsers.Datetime.Parse,
        hidden=True,
        help="""\
        The time when the cluster will be auto-deleted, such as
        "2017-08-29T18:52:51.142Z". See $ gcloud topic datetimes for
        information on time formats.
        """)
    auto_delete_group.add_argument(
        '--no-max-age',
        action='store_true',
        hidden=True,
        help="""\
        Cancels the cluster auto-deletion by maximum cluster age (configured by
         --max-age or --expiration-time flags)
        """)

    auto_delete_group.add_argument(
        '--delete-max-age',
        type=arg_parsers.Duration(),
        help="""\
        The lifespan of the cluster with auto-deletion upon completion,
        such as "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    auto_delete_group.add_argument(
        '--delete-expiration-time',
        type=arg_parsers.Datetime.Parse,
        help="""\
        The time when the cluster will be auto-deleted, such as
        "2017-08-29T18:52:51.142Z". See $ gcloud topic datetimes for
        information on time formats.
        """)
    auto_delete_group.add_argument(
        '--no-delete-max-age',
        action='store_true',
        help="""\
        Cancels the cluster auto-deletion by maximum cluster age (configured
        by --delete-max-age or --delete-expiration-time flags)
        """)

    idle_stop_group = parser.add_mutually_exclusive_group()
    idle_stop_group.add_argument(
        '--stop-max-idle',
        type=arg_parsers.Duration(),
        help="""\
        The duration after the last job completes to auto-stop the cluster,
        such as "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    idle_stop_group.add_argument(
        '--no-stop-max-idle',
        action='store_true',
        help="""\
        Cancels the cluster auto-stop by cluster idle duration (configured
        by --stop-max-idle flag)
        """)

    auto_stop_group = parser.add_mutually_exclusive_group()
    auto_stop_group.add_argument(
        '--stop-max-age',
        type=arg_parsers.Duration(),
        help="""\
        The lifespan of the cluster, with auto-stop upon completion,
        such as "2h" or "1d".
        See $ gcloud topic datetimes for information on duration formats.
        """)
    auto_stop_group.add_argument(
        '--stop-expiration-time',
        type=arg_parsers.Datetime.Parse,
        help="""\
        The time when the cluster will be auto-stopped, such as
        "2017-08-29T18:52:51.142Z". See $ gcloud topic datetimes for
        information on time formats.
        """)
    auto_stop_group.add_argument(
        '--no-stop-max-age',
        action='store_true',
        help="""\
        Cancels the cluster auto-stop by maximum cluster age (configured by
        --stop-max-age or --stop-expiration-time flags)
        """)

    # Can only specify one of --autoscaling-policy or --disable-autoscaling
    autoscaling_group = parser.add_mutually_exclusive_group()
    flags.AddAutoscalingPolicyResourceArgForCluster(
        autoscaling_group, api_version='v1')
    autoscaling_group.add_argument(
        '--disable-autoscaling',
        action='store_true',
        help="""\
        Disable autoscaling, if it is enabled. This is an alias for passing the
        empty string to --autoscaling-policy'.
        """)
    user_sa_mapping_util.AddUpdateUserSaMappingFlags(parser)

  def Run(self, args):
    dataproc = dp.Dataproc(self.ReleaseTrack())
    cluster_ref = args.CONCEPTS.cluster.Parse()

    cluster_config = dataproc.messages.ClusterConfig()
    changed_fields = []

    has_changes = False
    no_update_error_msg = (
        'Must specify at least one cluster parameter to update.'
    )

    if args.num_workers is not None:
      worker_config = dataproc.messages.InstanceGroupConfig(
          numInstances=args.num_workers)
      cluster_config.workerConfig = worker_config
      changed_fields.append('config.worker_config.num_instances')
      has_changes = True

    num_secondary_workers = _FirstNonNone(args.num_preemptible_workers,
                                          args.num_secondary_workers)
    if num_secondary_workers is not None:
      worker_config = dataproc.messages.InstanceGroupConfig(
          numInstances=num_secondary_workers)
      cluster_config.secondaryWorkerConfig = worker_config
      changed_fields.append(
          'config.secondary_worker_config.num_instances')
      has_changes = True

    if args.min_secondary_worker_fraction is not None:
      if cluster_config.secondaryWorkerConfig is None:
        worker_config = dataproc.messages.InstanceGroupConfig(
            startupConfig=dataproc.messages.StartupConfig(
                requiredRegistrationFraction=(
                    args.min_secondary_worker_fraction
                )
            )
        )
      else:
        worker_config = dataproc.messages.InstanceGroupConfig(
            numInstances=num_secondary_workers,
            startupConfig=dataproc.messages.StartupConfig(
                requiredRegistrationFraction=(
                    args.min_secondary_worker_fraction
                )
            ),
        )
      cluster_config.secondaryWorkerConfig = worker_config
      changed_fields.append(
          'config.secondary_worker_config.startup_config.required_registration_fraction'
      )
      has_changes = True

    if self.ReleaseTrack() == base.ReleaseTrack.ALPHA:
      if args.secondary_worker_standard_capacity_base is not None:
        if cluster_config.secondaryWorkerConfig is None:
          worker_config = dataproc.messages.InstanceGroupConfig(
              instanceFlexibilityPolicy=dataproc.messages.InstanceFlexibilityPolicy(
                  provisioningModelMix=dataproc.messages.ProvisioningModelMix(
                      standardCapacityBase=args.secondary_worker_standard_capacity_base
                  )))
        else:
          worker_config = dataproc.messages.InstanceGroupConfig(
              numInstances=num_secondary_workers,
              startupConfig=cluster_config.secondaryWorkerConfig.startupConfig,
              instanceFlexibilityPolicy=dataproc.messages.InstanceFlexibilityPolicy(
                  provisioningModelMix=dataproc.messages.ProvisioningModelMix(
                      standardCapacityBase=args.secondary_worker_standard_capacity_base
                  )
              )
          )
        cluster_config.secondaryWorkerConfig = worker_config
        changed_fields.append(
            'config.secondary_worker_config.instance_flexibility_policy.provisioning_model_mix.standard_capacity_base'
        )
        has_changes = True

    if args.autoscaling_policy:
      cluster_config.autoscalingConfig = dataproc.messages.AutoscalingConfig(
          policyUri=args.CONCEPTS.autoscaling_policy.Parse().RelativeName())
      changed_fields.append('config.autoscaling_config.policy_uri')
      has_changes = True
    elif args.autoscaling_policy == '' or args.disable_autoscaling:  # pylint: disable=g-explicit-bool-comparison
      # Disabling autoscaling. Don't need to explicitly set
      # cluster_config.autoscaling_config to None.
      changed_fields.append('config.autoscaling_config.policy_uri')
      has_changes = True

    lifecycle_config = dataproc.messages.LifecycleConfig()
    changed_config = False
    # Flags max_age, expiration_time, max_idle, no_max_age, no_max_idle are
    # hidden, but still supported. They are replaced with new flags
    # delete_max_age, delete_expiration_time, delete_max_idle,
    # no_delete_max_age and no_delete_max_idle.
    if args.max_age is not None:
      lifecycle_config.autoDeleteTtl = six.text_type(args.max_age) + 's'
      changed_fields.append('config.lifecycle_config.auto_delete_ttl')
      changed_config = True
    if args.expiration_time is not None:
      lifecycle_config.autoDeleteTime = times.FormatDateTime(
          args.expiration_time)
      changed_fields.append('config.lifecycle_config.auto_delete_time')
      changed_config = True
    if args.max_idle is not None:
      lifecycle_config.idleDeleteTtl = six.text_type(args.max_idle) + 's'
      changed_fields.append('config.lifecycle_config.idle_delete_ttl')
      changed_config = True
    if args.no_max_age:
      lifecycle_config.autoDeleteTtl = None
      changed_fields.append('config.lifecycle_config.auto_delete_ttl')
      changed_config = True
    if args.no_max_idle:
      lifecycle_config.idleDeleteTtl = None
      changed_fields.append('config.lifecycle_config.idle_delete_ttl')
      changed_config = True

    if args.delete_max_age is not None:
      lifecycle_config.autoDeleteTtl = (
          six.text_type(args.delete_max_age) + 's'
      )
      changed_fields.append('config.lifecycle_config.auto_delete_ttl')
      changed_config = True
    if args.delete_expiration_time is not None:
      lifecycle_config.autoDeleteTime = times.FormatDateTime(
          args.delete_expiration_time
      )
      changed_fields.append('config.lifecycle_config.auto_delete_time')
      changed_config = True
    if args.delete_max_idle is not None:
      lifecycle_config.idleDeleteTtl = (
          six.text_type(args.delete_max_idle) + 's'
      )
      changed_fields.append('config.lifecycle_config.idle_delete_ttl')
      changed_config = True
    if args.no_delete_max_age:
      lifecycle_config.autoDeleteTtl = None
      changed_fields.append('config.lifecycle_config.auto_delete_ttl')
      changed_config = True
    if args.no_delete_max_idle:
      lifecycle_config.idleDeleteTtl = None
      changed_fields.append('config.lifecycle_config.idle_delete_ttl')
      changed_config = True

    if args.stop_max_age is not None:
      lifecycle_config.autoStopTtl = six.text_type(args.stop_max_age) + 's'
      changed_fields.append('config.lifecycle_config.auto_stop_ttl')
      changed_config = True
    if args.stop_expiration_time is not None:
      lifecycle_config.autoStopTime = times.FormatDateTime(
          args.stop_expiration_time)
      changed_fields.append('config.lifecycle_config.auto_stop_time')
      changed_config = True
    if args.stop_max_idle is not None:
      lifecycle_config.idleStopTtl = six.text_type(args.stop_max_idle) + 's'
      changed_fields.append('config.lifecycle_config.idle_stop_ttl')
      changed_config = True
    if args.no_stop_max_age:
      lifecycle_config.autoStopTtl = None
      changed_fields.append('config.lifecycle_config.auto_stop_ttl')
      changed_config = True
    if args.no_stop_max_idle:
      lifecycle_config.idleStopTtl = None
      changed_fields.append('config.lifecycle_config.idle_stop_ttl')
      changed_config = True

    if changed_config:
      cluster_config.lifecycleConfig = lifecycle_config
      has_changes = True

    # Put in a thunk so we only make this call if needed
    def _GetCurrentLabels():
      # We need to fetch cluster first so we know what the labels look like. The
      # labels_util will fill out the proto for us with all the updates and
      # removals, but first we need to provide the current state of the labels
      current_cluster = _GetCurrentCluster(dataproc, cluster_ref)
      return current_cluster.labels
    labels_update = labels_util.ProcessUpdateArgsLazy(
        args, dataproc.messages.Cluster.LabelsValue,
        orig_labels_thunk=_GetCurrentLabels)
    if labels_update.needs_update:
      has_changes = True
      changed_fields.append('labels')
    labels = labels_update.GetOrNone()

    def _GetCurrentUserServiceAccountMapping():
      current_cluster = _GetCurrentCluster(dataproc, cluster_ref)
      if (
          current_cluster.config.securityConfig
          and current_cluster.config.securityConfig.identityConfig
      ):
        return (
            current_cluster.config.securityConfig.identityConfig.userServiceAccountMapping
        )
      return None

    def _UpdateSecurityConfig(cluster_config, user_sa_mapping):
      if cluster_config.securityConfig is None:
        cluster_config.securityConfig = dataproc.messages.SecurityConfig()
      if cluster_config.securityConfig.identityConfig is None:
        cluster_config.securityConfig.identityConfig = (
            dataproc.messages.IdentityConfig()
        )

      cluster_config.securityConfig.identityConfig.userServiceAccountMapping = (
          user_sa_mapping
      )

    if args.add_user_mappings or args.remove_user_mappings:
      if not _IsMultitenancyCluster(_GetCurrentCluster(dataproc, cluster_ref)):
        raise exceptions.ArgumentError(
            'User service account mapping can only be updated for multi-tenant'
            ' clusters.'
        )
      user_sa_mapping_update = user_sa_mapping_util.ProcessUpdateArgsLazy(
          args,
          dataproc.messages.IdentityConfig.UserServiceAccountMappingValue,
          orig_user_sa_mapping_thunk=_GetCurrentUserServiceAccountMapping,
      )
      if user_sa_mapping_update.needs_update:
        changed_fields.append(
            'config.security_config.identity_config.user_service_account_mapping'
        )
        has_changes = True
      else:
        if args.add_user_mappings:
          no_update_error_msg += (
              ' User to add is already present in service account mapping.'
          )
        if args.remove_user_mappings:
          no_update_error_msg += (
              ' User to remove is not present in service account mapping.'
          )
      user_sa_mapping = user_sa_mapping_update.GetOrNone()
      if user_sa_mapping:
        _UpdateSecurityConfig(cluster_config, user_sa_mapping)
    elif args.identity_config_file:
      if not _IsMultitenancyCluster(_GetCurrentCluster(dataproc, cluster_ref)):
        raise exceptions.ArgumentError(
            'User service account mapping can only be updated for multi-tenant'
            ' clusters.'
        )
      if cluster_config.securityConfig is None:
        cluster_config.securityConfig = dataproc.messages.SecurityConfig()
      cluster_config.securityConfig.identityConfig = (
          clusters.ParseIdentityConfigFile(dataproc, args.identity_config_file)
      )
      changed_fields.append(
          'config.security_config.identity_config.user_service_account_mapping'
      )
      has_changes = True

    if not has_changes:
      raise exceptions.ArgumentError(no_update_error_msg)

    cluster = dataproc.messages.Cluster(
        config=cluster_config,
        clusterName=cluster_ref.clusterName,
        labels=labels,
        projectId=cluster_ref.projectId)

    request = dataproc.messages.DataprocProjectsRegionsClustersPatchRequest(
        clusterName=cluster_ref.clusterName,
        region=cluster_ref.region,
        projectId=cluster_ref.projectId,
        cluster=cluster,
        updateMask=','.join(changed_fields),
        requestId=util.GetUniqueId())

    if args.graceful_decommission_timeout is not None:
      request.gracefulDecommissionTimeout = (
          six.text_type(args.graceful_decommission_timeout) + 's')

    operation = dataproc.client.projects_regions_clusters.Patch(request)

    if args.async_:
      log.status.write(
          'Updating [{0}] with operation [{1}].'.format(
              cluster_ref, operation.name))
      return

    util.WaitForOperation(
        dataproc,
        operation,
        message='Waiting for cluster update operation',
        timeout_s=args.timeout)

    request = dataproc.messages.DataprocProjectsRegionsClustersGetRequest(
        projectId=cluster_ref.projectId,
        region=cluster_ref.region,
        clusterName=cluster_ref.clusterName)
    cluster = dataproc.client.projects_regions_clusters.Get(request)
    log.UpdatedResource(cluster_ref)
    return cluster


def _FirstNonNone(first, second):
  return first if first is not None else second


def _AddAlphaArguments(parser, release_track):

  if release_track == base.ReleaseTrack.ALPHA:

    parser.add_argument(
        '--secondary-worker-standard-capacity-base',
        type=int,
        help="""
              The number of standard VMs in the Spot and Standard Mix
        feature.
              """,
    )


def _IsMultitenancyCluster(cluster) -> bool:
  """Checks if the cluster is a multi-tenant cluster.

  Args:
    cluster: The cluster configuration.

  Returns:
    True if the cluster is a multi-tenant cluster, False otherwise.
  """
  config = cluster.config
  if config and config.softwareConfig and config.softwareConfig.properties:
    props = config.softwareConfig.properties
    for prop in props.additionalProperties:
      if (
          prop.key == dataproc_constants.ENABLE_DYNAMIC_MULTI_TENANCY_PROPERTY
          and prop.value.lower() == 'true'
      ):
        return True
  return False


def _GetCurrentCluster(dataproc, cluster_ref):
  """Retrieves the current cluster configuration.

  Args:
    dataproc: The Dataproc API client.
    cluster_ref: The reference to the cluster.

  Returns:
    The current cluster configuration.
  """
  # This is used for labels and auxiliary_node_pool_configs
  get_cluster_request = (
      dataproc.messages.DataprocProjectsRegionsClustersGetRequest(
          projectId=cluster_ref.projectId,
          region=cluster_ref.region,
          clusterName=cluster_ref.clusterName,
      )
  )
  current_cluster = dataproc.client.projects_regions_clusters.Get(
      get_cluster_request
  )
  return current_cluster
