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
"""Command to list GDCE clusters."""

from apitools.base.py import list_pager
from googlecloudsdk.api_lib.edge_cloud.container import util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.edge_cloud.container import resource_args
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources

DETAILED_HELP = {
    'DESCRIPTION':
        """\
        List Edge Container clusters.
    """,
    'EXAMPLES':
        """\
    To list the clusters in region us-central1, run:

      $ {command} --location=us-central1
    """,
    'API REFERENCE':
        """\
    This command uses the edgecontainer/v1alpha API. The full documentation for\
    this API can be found at: https://cloud.google.com/edge-cloud
    """,
}

DISPLAY_TABLE = '''
      table(
        name.basename():label=NAME,
        endpoint:label=ENDPOINT,
        labels:label=LABELS,
        controlPlaneVersion:label=CONTROL_PLANE_VERSION,
        nodeVersion:label=NODE_VERSION,
        createTime.date():label=CREATED
      )
      '''

CLUSTERS_COLLECTION_NAME = 'edgecontainer.projects.locations.clusters'
V1_API_VERSION = 'v1'
V1_ALPHA_API_VERSION = 'v1alpha'

LOC_FLAG = '--location'
LOC_FLAG_HELP = ('Parent Edge Container location to list all contained Edge'
                 ' Container clusters.')

RCP_DEPRECATION_RELEASE_NOTES_LINK = (
    'https://cloud.google.com/distributed-cloud/edge/latest/docs/'
    'release-notes#March_14_2024')
DEPRECATION_WARNING_TEMPLATE = (
    'DEPRECATION: Cluster {} is hosting a control plane in the cloud, which is '
    'now deprecated. Please migrate all clusters to host the control plane '
    'locally on edge-cloud machines: ' + RCP_DEPRECATION_RELEASE_NOTES_LINK
)


def GetUriFromResourceFunc(api_version):
  def UriFunc(cluster, **kwargs):
    kwargs['api_version'] = api_version
    kwargs['collection'] = 'edgecontainer.projects.locations.clusters'
    return resources.REGISTRY.Parse(cluster.name, **kwargs).SelfLink()
  return UriFunc


def IsRCPCluster(cluster):
  return cluster.controlPlane is None or cluster.controlPlane.local is None


def PrintWarningsAndReturnTrue(cluster):
  if IsRCPCluster(cluster) and cluster.status != 'PROVISIONING':
    log.warning(DEPRECATION_WARNING_TEMPLATE.format(cluster.name))

  return True


# TODO(b/331978625): Unify GA in python after validating Alpha.
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class ListAlpha(base.ListCommand):
  """List Edge Container clusters."""

  detailed_help = DETAILED_HELP

  @staticmethod
  def Args(parser):
    """Register flags for this command.

    Args:
      parser: An argparse.ArgumentParser-like object. It is mocked out in order
        to capture some information, but behaves like an ArgumentParser.
    """
    resource_args.AddLocationOptionalResourceArgForListing(parser)
    parser.display_info.AddFormat(DISPLAY_TABLE)
    parser.display_info.AddUriFunc(GetUriFromResourceFunc(V1_ALPHA_API_VERSION))

  def Run(self, args):
    """This is what gets called when the user runs this command.

    Args:
      args: an argparse namespace. All the arguments that were provided to this
        command invocation.

    Returns:
      Some value that we want to have printed later.
    """
    cluster_client = util.GetClientInstance(self.ReleaseTrack())
    messages = util.GetMessagesModule(self.ReleaseTrack())

    vals = properties.VALUES
    project_id = args.project or vals.core.project.Get(required=True)
    location = args.location or vals.edge_container.location.Get(required=True)

    return list_pager.YieldFromList(
        cluster_client.projects_locations_clusters,
        messages.EdgecontainerProjectsLocationsClustersListRequest(
            parent=f'projects/{project_id}/locations/{location}',
            pageSize=args.page_size,
            filter=args.filter
        ),
        batch_size=args.page_size,
        field='clusters',
        limit=args.limit,
        batch_size_attribute='pageSize',
        predicate=PrintWarningsAndReturnTrue)
