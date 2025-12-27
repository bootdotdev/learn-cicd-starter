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

"""Command to update a cluster-director cluster resource."""

import textwrap

from googlecloudsdk.api_lib.hypercomputecluster import utils as api_utils
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.cluster_director.clusters import flags
from googlecloudsdk.command_lib.cluster_director.clusters import utils
from googlecloudsdk.core import log


DETAILED_HELP = {
    "DESCRIPTION": textwrap.dedent("""
        *{command}* facilitates the updation of a cluster resource.

        There are following ways to update a cluster:
        - [Preferred] Use granular flags to update cluster specs, based on read-modify-update pattern.
          - Read the existing cluster specs through `get` cluster request.
          - Modify the cluster specs through granular flags.
          - Update the cluster specs through `patch` cluster request.
        - Use --config with cluster specs and --update-mask flags, both in JSON format.
          - Map and repeated fields update requires existing and new values.
          - For e.g. if we want to update a cluster to add a new nodeset, then we will use the update_mask "orchestrator.slurm.node_sets", and the patch cluster must include all the existing nodesets as well as the new one.

        Please refer to the examples below for more details.
        """),
    "EXAMPLES": textwrap.dedent("""
        To update a cluster `my-cluster` in location `us-central1-a` with granular flags, run the following example:

        Add labels, compute instances, slurm node sets, slurm partitions and update description and default partition:

        $ {command} my-cluster --location us-central1-a \
        --description "My updated cluster description" \
        --add-labels env=prod,client=gcloud-cli \
        --add-on-demand-instances id=compute1,zone=us-central1-a,machineType=n2-standard-2 \
        --add-reserved-instances id=compute2,reservation=zones/us-central1-a/reservations/{reservation},machineType={machineType} \
        --add-spot-instances id=compute3,zone=us-central1-a,machineType=n2-standard-2 \
        --add-dws-flex-instances id=compute4,zone=us-central1-a,machineType=a4-highgpu-8g,maxDuration=10000s \
        --add-slurm-node-sets id=nodeset1,computeId=compute1 \
        --add-slurm-node-sets id=nodeset2,computeId=compute2 \
        --add-slurm-node-sets id=nodeset3,computeId=compute3 \
        --add-slurm-node-sets id=nodeset4,computeId=compute4 \
        --add-slurm-partitions id=partition1,nodesetIds=[nodeset1] \
        --add-slurm-partitions id=partition2,nodesetIds=[nodeset2,nodeset3,nodeset4] \
        --slurm-default-partition partition1

        Update slurm node sets and slurm partitions:

        $ {command} my-cluster --location us-central1-a \
        --update-slurm-node-sets id=nodeset1,staticNodeCount=2,maxDynamicNodeCount=10 \
        --update-slurm-partitions id=partition1,nodesetIds=[nodeset0],exclusive=true

        Remove slurm node sets, slurm partitions and compute instances and update default partition:

        $ {command} my-cluster --location us-central1-a \
        --slurm-default-partition partition0 \
        --remove-labels env,client \
        --remove-slurm-partitions partition1 \
        --remove-slurm-partitions partition2 \
        --remove-slurm-node-sets nodeset1 \
        --remove-slurm-node-sets nodeset2 \
        --remove-slurm-node-sets nodeset3 \
        --remove-slurm-node-sets nodeset4 \
        --remove-on-demand-instances compute1 \
        --remove-reserved-instances compute2 \
        --remove-spot-instances compute3 \
        --remove-dws-flex-instances compute4

        Or cluster `my-cluster` in location `us-central1-a` with config JSON run the following JSON example:

        $ {command} my-cluster --location=us-central1-a --update-mask=labels --config='{"key": "value"}'

        Or create a JSON file `my-cluster-config.json` with the cluster specs and run the following file example:

        $ {command} my-cluster --location=us-central1-a --update-mask=labels --config-from-file=my-cluster-config.json

        Or create a JSON file with the update mask and run the following file example:

        $ {command} my-cluster --location=us-central1-a --update-mask-from-file=my-update-mask.json --config-from-file=my-cluster-config.json
        """),
}


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class Update(base.UpdateCommand):
  """Updates a Cluster Director resource."""

  @classmethod
  def Args(cls, parser):
    """Specifies command flags.

    Args:
      parser: argparse.Parser: Parser object for command line inputs.
    """
    base.ASYNC_FLAG.AddToParser(parser)
    api_version = api_utils.GetApiVersion(cls.ReleaseTrack())
    utils.AddClusterNameArgToParser(parser=parser, api_version=api_version)
    group = parser.add_group(
        help="Cluster configuration for provisioning with updates.",
        mutex=True,
        required=True,
    )
    config_group = group.add_group(
        help="Cluster configuration for updates.",
    )
    flags.AddConfig(parser=config_group, api_version=api_version, required=True)
    flags.AddUpdateMask(
        parser=config_group, api_version=api_version, required=True
    )
    flag_group = group.add_group(
        help="Flag Configurations to define cluster updates.",
    )
    flags.AddDescription(parser=flag_group, api_version=api_version)
    flags.AddLabels(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddOnDemandInstances(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddSpotInstances(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddReservedInstances(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddDwsFlexInstances(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddSlurmNodeSets(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddSlurmPartitions(
        parser=flag_group, api_version=api_version, include_update_flags=True
    )
    flags.AddSlurmDefaultPartition(parser=flag_group, api_version=api_version)

  def Run(self, args):
    """Constructs and sends request.

    Args:
      args: argparse.Namespace, An object that contains the values for the
        arguments specified in the .Args() method.

    Returns:
      ProcessHttpResponse of the request made.
    """
    release_track = self.ReleaseTrack()
    client = api_utils.GetClientInstance(release_track)
    messages = api_utils.GetMessagesModule(release_track)
    existing_cluster = None
    if not args.IsSpecified("config"):
      existing_cluster = api_utils.GetCluster(client, args, messages)
    cluster_util = utils.ClusterUtil(
        args=args, message_module=messages, existing_cluster=existing_cluster
    )
    cluster_ref = cluster_util.cluster_ref

    if args.IsSpecified("config"):
      cluster_patch, update_mask = cluster_util.MakeClusterPatchFromConfig()
    else:
      cluster_patch, update_mask = cluster_util.MakeClusterPatch()

    operation = client.projects_locations_clusters.Patch(
        messages.HypercomputeclusterProjectsLocationsClustersPatchRequest(
            name=cluster_ref.RelativeName(),
            cluster=cluster_patch,
            updateMask=update_mask,
        )
    )
    log.status.Print(
        "Update request issued for: [{0}]".format(cluster_ref.Name())
    )
    if args.async_:
      return operation

    response = api_utils.WaitForOperation(
        client=client,
        operation=operation,
        message="Waiting for operation [{0}] to complete".format(
            operation.name
        ),
        max_wait_sec=3600,
    )
    log.status.Print("Updated cluster [{0}].".format(cluster_ref.Name()))
    return response


Update.detailed_help = DETAILED_HELP
