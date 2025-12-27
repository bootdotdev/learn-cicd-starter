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

"""Command to update snapshot settings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.snapshot_settings import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties
from googlecloudsdk.core import resources


@base.UniverseCompatible
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  """Update snapshot settings."""

  @staticmethod
  def Args(parser):
    flags.AddUpdateSnapshotSettingsStorageLocationFlags(parser)
    parser.display_info.AddFormat(
        'yaml(storageLocation.policy,'
        ' storageLocation.locations.list(show="keys"))'
    )

  def Run(self, args):
    return self._Run(args)

  def _Run(
      self,
      args,
      support_region=False,
  ):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    if support_region and args.region:
      # 1. Get the updated regional snapshot settings, we only support updating
      # access locations for now.
      new_locations_values = []
      access_location = client.messages.SnapshotSettingsAccessLocation()

      if args.add_access_locations:
        for location in args.add_access_locations:
          new_locations_values.append(
              client.messages.SnapshotSettingsAccessLocation.LocationsValue.AdditionalProperty(
                  key=location,
                  value=client.messages.SnapshotSettingsAccessLocationAccessLocationPreference(
                      region=location
                  ),
              )
          )

      if args.remove_access_locations:
        for location in args.remove_access_locations:
          new_locations_values.append(
              client.messages.SnapshotSettingsAccessLocation.LocationsValue.AdditionalProperty(
                  key=location,
                  value=client.messages.SnapshotSettingsAccessLocationAccessLocationPreference(),
              )
          )

      access_location.locations = (
          client.messages.SnapshotSettingsAccessLocation.LocationsValue(
              additionalProperties=new_locations_values
          )
      )

      if args.access_location_policy:
        new_policy = client.messages.SnapshotSettingsAccessLocation.PolicyValueValuesEnum(
            args.access_location_policy.upper().replace('-', '_')
        )
        access_location.policy = new_policy

      # 2. Patch the snapshot settings
      service = client.apitools_client.regionSnapshotSettings
      patch_request = client.messages.ComputeRegionSnapshotSettingsPatchRequest(
          snapshotSettings=client.messages.SnapshotSettings(
              accessLocation=access_location
          ),
          project=properties.VALUES.core.project.GetOrFail(),
          region=args.region,
          updateMask='accessLocation',
      )

      log.status.Print(
          'Request issued for: [{0}]'.format(
              properties.VALUES.core.project.GetOrFail()
          )
      )

      result = client.MakeRequests(
          [(service, 'Patch', patch_request)], no_followup=True
      )[0]
      operation_ref = resources.REGISTRY.Parse(
          result.name,
          params={
              'project': properties.VALUES.core.project.GetOrFail(),
              'region': args.region,
          },
          collection='compute.regionOperations',
      )
      if args.async_:
        log.UpdatedResource(
            operation_ref,
            kind='gce regional snapshot settings',
            is_async=True,
            details=(
                'Use [gcloud compute snapshot-settings describe'
                ' --region={region}] command to check the status of this'
                ' operation.'
            ),
        )
        return result
      snap_settings_ref = holder.resources.Parse(
          None,
          params={
              'project': properties.VALUES.core.project.GetOrFail,
              'region': args.region,
          },
          collection='compute.regionSnapshotSettings',
      )
      operation_poller = poller.Poller(
          holder.client.apitools_client.regionSnapshotSettings,
          snap_settings_ref,
      )
      waiter.WaitFor(
          operation_poller,
          operation_ref,
          'Waiting for operation [projects/{0}/region/{1}/operations/{2}] to'
          ' complete'.format(
              properties.VALUES.core.project.GetOrFail(),
              args.region,
              operation_ref.Name(),
          ),
      )

      log.status.Print(
          'Updated compute_project [{0}].'.format(
              properties.VALUES.core.project.GetOrFail()
          )
      )
      # 5. Get the updated regional snapshot settings
      service = client.apitools_client.regionSnapshotSettings
      get_request = client.messages.ComputeRegionSnapshotSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail(),
          region=args.region,
      )
      result = client.MakeRequests(
          [(service, 'Get', get_request)], no_followup=True
      )[0]
      return result

    else:
      # 1. Get the update mask:
      # If storage location policy is specified, then the update mask is
      # adjusted so that the whole storage location structure is replaced.
      # If a storage location name is specified, then the update mask is
      # specified so that other storage location names are clearead.
      if args.storage_location_policy:
        update_mask = 'storageLocation'
      elif args.storage_location_names:
        update_mask = 'storageLocation.locations'
      else:
        raise ValueError('Must specify at least one valid parameter to update.')

      update_snapshot_settings = client.messages.SnapshotSettings()
      # 2. Get the updated policy
      if args.storage_location_policy:
        new_policy = client.messages.SnapshotSettingsStorageLocationSettings.PolicyValueValuesEnum(
            args.storage_location_policy.upper().replace('-', '_')
        )
        update_snapshot_settings.storageLocation = (
            client.messages.SnapshotSettingsStorageLocationSettings(
                policy=new_policy
            )
        )

      # 3. Get the updated locations
      if args.storage_location_names:
        if len(args.storage_location_names) != 1:
          raise ValueError(
              'Invalid value for [storage_location_names]: only a single'
              ' location name is permitted at this time'
          )
        new_locations_values = [
            client.messages.SnapshotSettingsStorageLocationSettings.LocationsValue.AdditionalProperty(
                key=args.storage_location_names[0],
                value=client.messages.SnapshotSettingsStorageLocationSettingsStorageLocationPreference(
                    name=args.storage_location_names[0]
                ),
            )
        ]
        if update_snapshot_settings.storageLocation is None:
          update_snapshot_settings.storageLocation = (
              client.messages.SnapshotSettingsStorageLocationSettings()
          )
        update_snapshot_settings.storageLocation.locations = client.messages.SnapshotSettingsStorageLocationSettings.LocationsValue(
            additionalProperties=new_locations_values
        )

      # 4. Patch the snapshot settings
      service = client.apitools_client.snapshotSettings
      patch_request = client.messages.ComputeSnapshotSettingsPatchRequest(
          snapshotSettings=update_snapshot_settings,
          project=properties.VALUES.core.project.GetOrFail(),
          updateMask=update_mask,
      )
      log.status.Print(
          'Request issued for: [{0}]'.format(
              properties.VALUES.core.project.GetOrFail()
          )
      )
      result = client.MakeRequests(
          [(service, 'Patch', patch_request)], no_followup=True
      )[0]
      operation_ref = resources.REGISTRY.Parse(
          result.name,
          params={
              'project': properties.VALUES.core.project.GetOrFail(),
          },
          collection='compute.globalOperations',
      )
      if args.async_:
        log.UpdatedResource(
            operation_ref,
            kind='gce global snapshot settings',
            is_async=True,
            details=(
                'Use [gcloud compute snapshot-settings describe] command to'
                ' check the status of this operation.'
            ),
        )
        return result
      snap_settings_ref = holder.resources.Parse(
          None,
          params={
              'project': properties.VALUES.core.project.GetOrFail,
          },
          collection='compute.snapshotSettings',
      )
      operation_poller = poller.Poller(
          holder.client.apitools_client.snapshotSettings,
          snap_settings_ref,
      )
      waiter.WaitFor(
          operation_poller,
          operation_ref,
          'Waiting for operation [projects/{0}/global/operations/{1}] to'
          ' complete'.format(
              properties.VALUES.core.project.GetOrFail(), operation_ref.Name()
          ),
      )
      log.status.Print(
          'Updated compute_project [{0}].'.format(
              properties.VALUES.core.project.GetOrFail()
          )
      )
      # 5. Get the updated snapshot settings
      service = client.apitools_client.snapshotSettings
      get_request = client.messages.ComputeSnapshotSettingsGetRequest(
          project=properties.VALUES.core.project.GetOrFail()
      )
      result = client.MakeRequests(
          [(service, 'Get', get_request)], no_followup=True
      )[0]
      return result


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.UniverseCompatible
class UpdateAlphaAndBeta(Update):
  """Update snapshot settings."""

  @staticmethod
  def Args(parser):
    flags.AddUpdateSnapshotSettingsAccessLocationFlags(parser)
    flags.AddUpdateSnapshotSettingsStorageLocationFlags(parser)
    flags.AddSnapshotSettingArg(parser)
    parser.display_info.AddFormat(
        'yaml(accessLocation.policy,'
        'accessLocation.locations.list(show="keys"),storageLocation.policy,'
        'storageLocation.locations.list(show="keys"))'
    )

  def Run(self, args):
    return self._Run(
        args,
        support_region=True,
    )


Update.detailed_help = {
    'brief': 'Update snapshot settings.',
    'DESCRIPTION': """\
      Update the snapshot settings of a project.
      """,
    'EXAMPLES': """\
    To update the snapshot settings and set the storage location policy to the
    nearest multi-region as the source disk, run:

          $ {command} --storage-location-policy=nearest-multi-region

    To update the snapshot settings and set the storage location policy to the
    same region as the source disk, run:

          $ {command} --storage-location-policy=local-region

    To update the snapshot settings and set the storage location policy to
    store snapshots in a specific location like `us-west1`, run:

          $ {command} --storage-location-policy=specific-locations \
              --storage-location-names=us-west1
     """,
    'API REFERENCE': """\
      This command uses the compute/alpha or compute/beta or compute/v1 API. The full documentation for this API
     can be found at: https://cloud.google.com/compute/""",
}
