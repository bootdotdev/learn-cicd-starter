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

"""Command to update disk settings."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute.disk_settings import flags
from googlecloudsdk.core import log
from googlecloudsdk.core import properties


@base.ReleaseTracks(base.ReleaseTrack.ALPHA, base.ReleaseTrack.BETA)
@base.UniverseCompatible
class Update(base.UpdateCommand):
  """Update disk settings."""

  detailed_help = {'EXAMPLES': """
        To update the disk settings in zone us-west1-a, add the access location ``us-central1 `` and remove the access location ``us-central2``
        in the project ``my-gcp-project'', run:

          $ {command} --add-access-locations=us-central1 --remove-access-locations=us-central2 --project=my-gcp-project --zone=us-west1-a
      """}

  @staticmethod
  def Args(parser):
    flags.AddDiskSettingArg(parser)
    flags.AddUpdateDiskSettingsFlags(parser)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    # 1. Get the updated disk settings, we only support updating access
    # locations for now.
    new_locations_values = []
    access_location = client.messages.DiskSettingsAccessLocation()
    if args.add_access_locations:
      for location in args.add_access_locations:
        new_locations_values.append(
            client.messages.DiskSettingsAccessLocation.LocationsValue.AdditionalProperty(
                key=location,
                value=client.messages.DiskSettingsAccessLocationAccessLocationPreference(
                    region=location
                ),
            )
        )

    if args.remove_access_locations:
      for location in args.remove_access_locations:
        new_locations_values.append(
            client.messages.DiskSettingsAccessLocation.LocationsValue.AdditionalProperty(
                key=location,
                value=client.messages.DiskSettingsAccessLocationAccessLocationPreference(),
            )
        )

    access_location.locations = (
        client.messages.DiskSettingsAccessLocation.LocationsValue(
            additionalProperties=new_locations_values
        )
    )
    if args.access_location_policy:
      new_policy = (
          client.messages.DiskSettingsAccessLocation.PolicyValueValuesEnum(
              args.access_location_policy.upper().replace('-', '_')
          )
      )
      access_location.policy = new_policy

    # 2. Patch the disk settings
    if args.zone:
      service = client.apitools_client.diskSettings
      patch_request = client.messages.ComputeDiskSettingsPatchRequest(
          diskSettings=client.messages.DiskSettings(
              accessLocation=access_location
          ),
          project=properties.VALUES.core.project.GetOrFail(),
          updateMask='accessLocation',
          zone=args.zone,
      )
      result = client.MakeRequests(
          [(service, 'Patch', patch_request)], no_followup=True
      )[0]
      operation_ref = holder.resources.Parse(
          result.name,
          params={
              'project': properties.VALUES.core.project.GetOrFail(),
              'zone': args.zone,
          },
          collection='compute.zoneOperations',
      )
      disk_settings_ref = holder.resources.Parse(
          None,
          params={
              'project': properties.VALUES.core.project.GetOrFail,
              'zone': args.zone,
          },
          collection='compute.diskSettings',
      )
      operation_poller = poller.Poller(
          holder.client.apitools_client.diskSettings,
          disk_settings_ref,
      )
      waiter.WaitFor(
          operation_poller,
          operation_ref,
          'Waiting for operation [projects/{0}/zones/{1}/operations/{2}] to'
          ' complete'.format(
              properties.VALUES.core.project.GetOrFail(),
              args.zone,
              operation_ref.Name(),
          ),
      )

      log.status.Print(
          'Updated zonal disk settings for compute_project [{0}] in zone [{1}].'
          .format(
              properties.VALUES.core.project.GetOrFail(),
              args.zone,
          )
      )
      return result
    else:
      service = client.apitools_client.regionDiskSettings
      patch_request = client.messages.ComputeRegionDiskSettingsPatchRequest(
          diskSettings=client.messages.DiskSettings(
              accessLocation=access_location
          ),
          project=properties.VALUES.core.project.GetOrFail(),
          region=args.region,
          updateMask='accessLocation',
      )
      result = client.MakeRequests(
          [(service, 'Patch', patch_request)], no_followup=True
      )[0]
      operation_ref = holder.resources.Parse(
          result.name,
          params={
              'project': properties.VALUES.core.project.GetOrFail(),
              'region': args.region,
          },
          collection='compute.regionOperations',
      )
      disk_settings_ref = holder.resources.Parse(
          None,
          params={
              'project': properties.VALUES.core.project.GetOrFail,
              'region': args.region,
          },
          collection='compute.regionDiskSettings',
      )
      operation_poller = poller.Poller(
          holder.client.apitools_client.regionDiskSettings,
          disk_settings_ref,
      )
      waiter.WaitFor(
          operation_poller,
          operation_ref,
          'Waiting for operation [projects/{0}/regions/{1}/operations/{2}] to'
          ' complete'.format(
              properties.VALUES.core.project.GetOrFail(),
              args.region,
              operation_ref.Name(),
          ),
      )

      log.status.Print(
          'Updated regional disk settings for compute_project [{0}] in region'
          ' [{1}].'.format(
              properties.VALUES.core.project.GetOrFail(),
              args.region,
          )
      )
      return result
