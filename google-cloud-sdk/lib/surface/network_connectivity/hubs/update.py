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


"""Command for updating hubs."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_api
from googlecloudsdk.api_lib.network_connectivity import networkconnectivity_util
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.network_connectivity import flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log
from googlecloudsdk.core import resources


def UpdatedPscFields(args, export_psc_config):
  """UpdatedPscFields returns the updated PSC field values.

  This method uses the existing hub and the flags to determine the new values.

  Args:
    args: The arguments that the user specified.
    export_psc_config: The existing hub's exportPscConfig.

  Returns:
    A tuple of the updated exportPsc field and updated exportPscConfig field.
  """
  # If the user did not specify any PSC flags, we can return early.
  if not (
      args.IsSpecified('export_psc')
      or args.IsSpecified(
          'export_psc_published_services_and_regional_google_apis'
      )
      or args.IsSpecified('export_psc_global_google_apis')
  ):
    return None, None

  # Handle the case where export_psc_config is None. This will happen if the
  # user does not have the NCC_PSC_GAPI visiblity label: b/391865147#comment29.
  # TODO: b/406009715 - Remove this once the API is GA.
  if export_psc_config is None:
    return args.export_psc, None

  # Check if this is the legacy case. We can ignore the other flags because the
  # mutex group ensures that the other flags are not set.
  if args.export_psc is not None:
    if args.export_psc:
      # If true, enable only PSC-ILB propagation.
      export_psc_config.publishedServicesAndRegionalGoogleApis = True
      return True, export_psc_config

    # If false, disable PSC-ILB and PSC-GAPI propagation.
    export_psc_config.publishedServicesAndRegionalGoogleApis = False
    export_psc_config.globalGoogleApis = False
    return False, export_psc_config

  # If this is not the legacy case, handle the new PSC flags.
  # 1. Update the new exportPscConfig values if they are set.
  if args.export_psc_published_services_and_regional_google_apis is not None:
    export_psc_config.publishedServicesAndRegionalGoogleApis = (
        args.export_psc_published_services_and_regional_google_apis
    )
  if args.export_psc_global_google_apis is not None:
    export_psc_config.globalGoogleApis = args.export_psc_global_google_apis

  # 2. If either of the values in the updated exportPscConfig are true, then set
  # exportPsc to true. Otherwise, set exportPsc to false.
  updated_export_psc = (
      export_psc_config.publishedServicesAndRegionalGoogleApis
      or export_psc_config.globalGoogleApis
  )
  return updated_export_psc, export_psc_config


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class Update(base.Command):
  """Update a hub.

  Update the details of a hub.
  """

  @staticmethod
  def Args(parser):
    flags.AddHubResourceArg(parser, 'to be updated')
    flags.AddDescriptionFlag(parser, 'New description of the hub.')
    flags.AddPscGroup(parser)
    flags.AddAsyncFlag(parser)
    labels_util.AddUpdateLabelsFlags(parser)

  def Run(self, args):
    client = networkconnectivity_api.HubsClient(
        release_track=self.ReleaseTrack()
    )
    hub_ref = args.CONCEPTS.hub.Parse()
    update_mask = []
    description = args.description
    if description is not None:
      update_mask.append('description')

    # Fetch the hub so we can update the PSC fields.
    original_hub = client.Get(hub_ref)
    updated_export_psc, updated_export_psc_config = UpdatedPscFields(
        args, original_hub.exportPscConfig
    )
    # We use both the export_psc field and the new export_psc_config, so we need
    # to include both in the mask.
    if updated_export_psc is not None:
      update_mask.append('exportPsc')
      update_mask.append('exportPscConfig')

    # Update the labels (using the original hub as well).
    labels = None
    labels_diff = labels_util.Diff.FromUpdateArgs(args)
    if labels_diff.MayHaveUpdates():
      labels_update = labels_diff.Apply(
          client.messages.GoogleCloudNetworkconnectivityV1betaHub.LabelsValue,
          original_hub.labels,
      )
      if labels_update.needs_update:
        labels = labels_update.labels
        update_mask.append('labels')

    hub = client.messages.GoogleCloudNetworkconnectivityV1betaHub(
        description=description,
        exportPsc=updated_export_psc,
        exportPscConfig=updated_export_psc_config,
        labels=labels,
    )
    op_ref = client.UpdateHubBeta(hub_ref, hub, update_mask)

    log.status.Print('Update request issued for: [{}]'.format(hub_ref.Name()))

    if args.async_:
      log.status.Print('Check operation [{}] for status.'.format(op_ref.name))
      return op_ref

    op_resource = resources.REGISTRY.ParseRelativeName(
        op_ref.name,
        collection='networkconnectivity.projects.locations.operations',
        api_version=networkconnectivity_util.VERSION_MAP[self.ReleaseTrack()],
    )
    poller = waiter.CloudOperationPoller(
        client.hub_service, client.operation_service
    )

    if op_ref.done:
      log.UpdatedResource(hub_ref.Name(), kind='hub')
      return poller.GetResult(op_resource)

    res = waiter.WaitFor(
        poller,
        op_resource,
        'Waiting for operation [{}] to complete'.format(op_ref.name),
        max_wait_ms=3600000,  # 1 hour
    )
    log.UpdatedResource(hub_ref.Name(), kind='hub')
    return res


Update.detailed_help = {
    'EXAMPLES': """ \
  To update the description of a hub named ``my-hub'', run:

    $ {command} my-hub --description="The new description of my-hub".
  """,
    'API REFERENCE': """ \
  This command uses the networkconnectivity/v1beta API. The full documentation
  for this API can be found at:
  https://cloud.google.com/network-connectivity/docs/reference/networkconnectivity/rest
  """,
}
