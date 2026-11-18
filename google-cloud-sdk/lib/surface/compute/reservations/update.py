# -*- coding: utf-8 -*- #
# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Command for compute reservations update."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import request_helper
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.reservations import flags as r_flags
from googlecloudsdk.command_lib.compute.reservations import resource_args
from googlecloudsdk.command_lib.compute.reservations import util


def _ValidateArgs(
    args,
    support_share_with_flag,
    support_auto_delete=False,
    support_reservation_sharing_policy=False,
    support_emergent_maintenance=False,
    support_share_type=False,
    support_scheduling_type=False,
):
  """Validates that both share settings arguments are mentioned.

  Args:
    args: The arguments given to the update command.
    support_share_with_flag: Check if share_with is supported.
    support_auto_delete: Check if auto-delete settings are supported.
    support_reservation_sharing_policy: Check if reservation sharing policy is
      supported.
    support_emergent_maintenance: Check if emergent maintenance is supported.
    support_share_type: Check if share setting is supported.
    support_scheduling_type: Check if scheduling type is supported.
  """
  # Check the version and share-with option.
  share_with = False
  parameter_names = [
      '--share-with',
      '--vm-count',
  ]
  one_option_exception_message = (
      'Please provide one of these options: 1- Specify share-with or'
      ' add-share-with or remove-share-with to update the project list. 2-'
      ' Specify reservation vm-count to resize. '
  )

  if support_auto_delete:
    parameter_names.extend([
        '--delete-at-time',
        '--delete-after-duration',
        '--disable-auto-delete',
    ])
    one_option_exception_message += (
        '3- Modify auto-delete'
        ' properties with specifing auto-delete-at-time or'
        ' auto-delete-after-duration or disable-auto-delete flags.'
    )
  if support_reservation_sharing_policy:
    parameter_names.extend([
        '--reservation-sharing-policy',
    ])
    one_option_exception_message += (
        '4- Modify reservation sharing policy with specifying'
        ' reservation-sharing-policy flag.'
    )
  if support_emergent_maintenance:
    parameter_names.extend([
        '--enable-emergent-maintenance',
        '--no-enable-emergent-maintenance'
    ])
    one_option_exception_message += (
        '5- Modify emergent maintenance with specifying'
        ' enable-emergent-maintenance flag.'
    )
  if support_share_type:
    parameter_names.extend([
        '--share-setting',
    ])
    one_option_exception_message += (
        '6- Modify share setting with specifying share-setting flag.'
    )
  if support_scheduling_type:
    parameter_names.extend([
        '--scheduling-type',
    ])
    one_option_exception_message += (
        '7- Modify scheduling type with specifying scheduling-type flag.'
    )

  has_share_with = False
  if support_share_with_flag:
    has_share_with = args.IsSpecified('share_with')
  has_add_share_with = args.IsSpecified('add_share_with')
  has_remove_share_with = args.IsSpecified('remove_share_with')
  if has_share_with or has_add_share_with or has_remove_share_with:
    share_with = True
  if (
      (has_share_with and has_add_share_with)
      or (has_share_with and has_remove_share_with)
      or (has_add_share_with and has_remove_share_with)
  ):
    raise exceptions.ConflictingArgumentsException(
        '--share-with', '--add-share-with', '--remove-share-with'
    )
  if has_remove_share_with:
    for project in getattr(args, 'remove_share_with', []):
      if not project.isnumeric():
        raise exceptions.InvalidArgumentException(
            '--remove-share-with',
            'Please specify project number (not project id/name).',
        )

  minimum_argument_specified = not share_with and not args.IsSpecified(
      'vm_count'
  )

  if support_auto_delete:
    auto_delete_settings_updated = args.IsSpecified('delete_at_time') or (
        args.IsSpecified('delete_after_duration')
        or args.IsSpecified('disable_auto_delete')
    )
    minimum_argument_specified = (
        minimum_argument_specified and not auto_delete_settings_updated
    )
  if support_reservation_sharing_policy:
    minimum_argument_specified = (
        minimum_argument_specified
        and not args.IsSpecified('reservation_sharing_policy')
    )
  if support_emergent_maintenance:
    minimum_argument_specified = (
        minimum_argument_specified
        and not args.IsSpecified('enable_emergent_maintenance')
    )
  if support_scheduling_type:
    minimum_argument_specified = (
        minimum_argument_specified and not args.IsSpecified('scheduling_type')
    )

  # Check parameters (add_share_with and remove_share_with are on GA).
  if minimum_argument_specified:
    raise exceptions.MinimumArgumentException(parameter_names,
                                              one_option_exception_message)


def _GetShareSettingUpdateRequest(
    args, reservation_ref, holder, support_share_with_flag,
    support_share_type):
  """Create Update Request for share-with.

  Returns:
  update request.
  Args:
   args: The arguments given to the update command.
   reservation_ref: reservation refrence.
   holder: base_classes.ComputeApiHolder.
   support_share_with_flag: Check if share_with is supported.
   support_share_type: Check if share_type is supported.
  """
  messages = holder.client.messages
  # Set updated properties and build update mask.
  share_settings = None
  update_mask = []
  setting_configs = None
  if support_share_type and args.IsSpecified('share_setting'):
    setting_configs = getattr(args, 'share_setting', None)
    update_mask.append('shareSettings.shareType')

  if support_share_with_flag:
    if not setting_configs and (args.IsSpecified('share_with') or
                                args.IsSpecified('add_share_with') or
                                args.IsSpecified('remove_share_with')):
      setting_configs = 'projects'

    if args.IsSpecified('share_with'):
      share_settings = util.MakeShareSettingsWithArgs(
          messages, args, setting_configs, share_with='share_with')
      update_mask.extend([
          'shareSettings.projectMap.' + project
          for project in getattr(args, 'share_with', [])
      ])
  else:
    setting_configs = 'projects'
  if args.IsSpecified('add_share_with'):
    share_settings = util.MakeShareSettingsWithArgs(
        messages, args, setting_configs, share_with='add_share_with')
    update_mask.extend([
        'shareSettings.projectMap.' + project
        for project in getattr(args, 'add_share_with', [])
    ])
  elif args.IsSpecified('remove_share_with'):
    share_settings = util.MakeShareSettingsWithArgs(
        messages, args, setting_configs, share_with='remove_share_with')
    update_mask.extend([
        'shareSettings.projectMap.' + project
        for project in getattr(args, 'remove_share_with', [])
    ])

  # Build reservation object using new share-settings.
  r_resource = util.MakeReservationMessage(messages, reservation_ref.Name(),
                                           share_settings, None, None, None,
                                           reservation_ref.zone)
  # Build update request.
  r_update_request = messages.ComputeReservationsUpdateRequest(
      reservation=reservation_ref.Name(),
      reservationResource=r_resource,
      paths=update_mask,
      project=reservation_ref.project,
      zone=reservation_ref.zone)

  return r_update_request


def _GetReservationSharingPolicyUpdateRequest(args, reservation_ref, holder):
  """Create Update Request for the reservation sharing policy.

  Returns:
    UpdateRequest
  Args:
    args: The arguments given to the update command.
    reservation_ref: reservation refrence.
    holder: base_classes.ComputeApiHolder.
  """
  messages = holder.client.messages

  r_resource = util.MakeReservationMessage(
      messages,
      reservation_ref.Name(),
      None,
      None,
      None,
      None,
      reservation_ref.zone,
      reservation_sharing_policy=getattr(
          args, 'reservation_sharing_policy', None
      ),
  )
  # Build update request.
  return messages.ComputeReservationsUpdateRequest(
      reservation=reservation_ref.Name(),
      reservationResource=r_resource,
      paths=['reservationSharingPolicy.serviceShareType'],
      project=reservation_ref.project,
      zone=reservation_ref.zone,
  )


def _GetResizeRequest(args, reservation_ref, holder):
  """Create Update Request for vm_count.

  Returns:
  resize request.
  Args:
   args: The arguments given to the update command.
   reservation_ref: reservation refrence.
   holder: base_classes.ComputeApiHolder.
  """
  messages = holder.client.messages
  vm_count = None
  if args.IsSpecified('vm_count'):
    vm_count = args.vm_count

  # Build resize request.
  r_resize_request = messages.ComputeReservationsResizeRequest(
      reservation=reservation_ref.Name(),
      reservationsResizeRequest=messages.ReservationsResizeRequest(
          specificSkuCount=vm_count),
      project=reservation_ref.project,
      zone=reservation_ref.zone)

  return r_resize_request


def _AutoDeleteUpdateRequest(args, reservation_ref, holder):
  """Create Update Request for modifying auto-delete properties."""
  messages = holder.client.messages

  update_mask = []

  if args.IsSpecified('delete_at_time'):
    update_mask.append('deleteAtTime')
    delete_at_time = args.delete_at_time
  else:
    delete_at_time = None

  if args.IsSpecified('delete_after_duration'):
    update_mask.append('deleteAfterDuration')
    delete_after_duration = args.delete_after_duration
  else:
    delete_after_duration = None

  if args.IsSpecified('disable_auto_delete'):
    update_mask.append('deleteAtTime')

  r_resource = util.MakeReservationMessage(
      messages,
      reservation_ref.Name(),
      None,
      None,
      None,
      None,
      reservation_ref.zone,
      delete_at_time,
      delete_after_duration,
  )

  # Build update request.
  return messages.ComputeReservationsUpdateRequest(
      reservation=reservation_ref.Name(),
      reservationResource=r_resource,
      paths=update_mask,
      project=reservation_ref.project,
      zone=reservation_ref.zone,
  )


def _EnableEmergentMaintenanceUpdateRequest(args, reservation_ref, holder):
  """Create Update Request for enabling emergent maintenance."""
  messages = holder.client.messages

  update_mask = []
  if args.IsSpecified('enable_emergent_maintenance'):
    update_mask.append('enableEmergentMaintenance')
    enable_emergent_maintenance = args.enable_emergent_maintenance
  else:
    enable_emergent_maintenance = None

  r_resource = util.MakeReservationMessage(
      messages,
      reservation_ref.Name(),
      None,
      None,
      None,
      None,
      reservation_ref.zone,
      enable_emergent_maintenance=enable_emergent_maintenance,
  )

  # Build Update Request.
  return messages.ComputeReservationsUpdateRequest(
      reservation=reservation_ref.Name(),
      reservationResource=r_resource,
      paths=update_mask,
      project=reservation_ref.project,
      zone=reservation_ref.zone,
  )


def _SchedulingTypeUpdateRequest(args, reservation_ref, holder):
  """Create Update Request for scheduling type."""
  messages = holder.client.messages
  update_mask = []
  if args.IsSpecified('scheduling_type'):
    update_mask.append('schedulingType')
    scheduling_type = args.scheduling_type
  else:
    scheduling_type = None
  r_resource = util.MakeReservationMessage(
      messages,
      reservation_ref.Name(),
      None,
      None,
      None,
      None,
      reservation_ref.zone,
      scheduling_type=scheduling_type,
  )

  # Build Update Request.
  return messages.ComputeReservationsUpdateRequest(
      reservation=reservation_ref.Name(),
      reservationResource=r_resource,
      paths=update_mask,
      project=reservation_ref.project,
      zone=reservation_ref.zone,
  )


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Update(base.UpdateCommand):
  """Update Compute Engine reservations."""
  _support_share_with_flag = False
  _support_auto_delete = False
  _support_reservation_sharing_policy = True
  _support_emergent_maintenance = True
  _support_share_type = False
  _support_scheduling_type = True

  @classmethod
  def Args(cls, parser):
    resource_args.GetReservationResourceArg().AddArgument(
        parser, operation_type='update')
    r_flags.GetAddShareWithFlag().AddToParser(parser)
    r_flags.GetRemoveShareWithFlag().AddToParser(parser)
    r_flags.GetVmCountFlag(False).AddToParser(parser)
    r_flags.GetReservationSharingPolicyFlag().AddToParser(parser)
    r_flags.GetEnableEmergentMaintenanceFlag().AddToParser(parser)
    r_flags.GetSchedulingTypeFlag().AddToParser(parser)

  def Run(self, args):
    """Common routine for updating reservation."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    resources = holder.resources
    service = holder.client.apitools_client.reservations

    # Validate the command.
    _ValidateArgs(
        args,
        self._support_share_with_flag,
        self._support_auto_delete,
        self._support_reservation_sharing_policy,
        self._support_emergent_maintenance,
        self._support_share_type,
        self._support_scheduling_type,
    )
    reservation_ref = resource_args.GetReservationResourceArg(
    ).ResolveAsResource(
        args,
        resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client))

    result = list()
    errors = []
    share_with = False
    if args.IsSpecified('add_share_with') or args.IsSpecified(
        'remove_share_with'):
      share_with = True
    if self._support_share_with_flag:
      if args.IsSpecified('share_with'):
        share_with = True

    if share_with:
      r_update_request = _GetShareSettingUpdateRequest(
          args, reservation_ref, holder, self._support_share_with_flag,
          self._support_share_type)
      # Invoke Reservation.update API.
      result.append(
          list(
              request_helper.MakeRequests(
                  requests=[(service, 'Update', r_update_request)],
                  http=holder.client.apitools_client.http,
                  batch_url=holder.client.batch_url,
                  errors=errors)))
      if errors:
        utils.RaiseToolException(errors)

    if self._support_reservation_sharing_policy:
      if args.IsSpecified('reservation_sharing_policy'):
        r_sharing_policy_request = _GetReservationSharingPolicyUpdateRequest(
            args, reservation_ref, holder
        )
        result.append(
            list(
                request_helper.MakeRequests(
                    requests=[(service, 'Update', r_sharing_policy_request)],
                    http=holder.client.apitools_client.http,
                    batch_url=holder.client.batch_url,
                    errors=errors,
                )
            )
        )

    if args.IsSpecified('vm_count'):
      r_resize_request = _GetResizeRequest(args, reservation_ref, holder)
      # Invoke Reservation.resize API.
      result.append(
          holder.client.MakeRequests(([(service, 'Resize', r_resize_request)])))

    if self._support_auto_delete:
      if args.IsSpecified('delete_at_time') or (
          args.IsSpecified('delete_after_duration')
          or args.IsSpecified('disable_auto_delete')
      ):
        r_update_request = _AutoDeleteUpdateRequest(
            args, reservation_ref, holder
        )

        result.append(
            list(
                request_helper.MakeRequests(
                    requests=[(service, 'Update', r_update_request)],
                    http=holder.client.apitools_client.http,
                    batch_url=holder.client.batch_url,
                    errors=errors,
                )
            )
        )
        if errors:
          utils.RaiseToolException(errors)

    if self._support_emergent_maintenance:
      if args.IsSpecified('enable_emergent_maintenance'):
        r_update_request = _EnableEmergentMaintenanceUpdateRequest(
            args, reservation_ref, holder
        )
        result.append(
            list(
                request_helper.MakeRequests(
                    requests=[(service, 'Update', r_update_request)],
                    http=holder.client.apitools_client.http,
                    batch_url=holder.client.batch_url,
                    errors=errors,
                )))
        if errors:
          utils.RaiseToolException(errors)

    if self._support_scheduling_type:
      if args.IsSpecified('scheduling_type'):
        r_update_request = _SchedulingTypeUpdateRequest(
            args, reservation_ref, holder
        )
        result.append(
            list(
                request_helper.MakeRequests(
                    requests=[(service, 'Update', r_update_request)],
                    http=holder.client.apitools_client.http,
                    batch_url=holder.client.batch_url,
                    errors=errors,
                )
            )
        )
        if errors:
          utils.RaiseToolException(errors)

    return result


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  """Update Compute Engine reservations."""
  _support_share_with_flag = True
  _support_auto_delete = True
  _support_reservation_sharing_policy = True
  _support_emergent_maintenance = True
  _support_share_type = True
  _support_scheduling_type = True

  @classmethod
  def Args(cls, parser):
    resource_args.GetReservationResourceArg().AddArgument(
        parser, operation_type='update')
    r_flags.GetShareWithFlag().AddToParser(parser)
    r_flags.GetAddShareWithFlag().AddToParser(parser)
    r_flags.GetRemoveShareWithFlag().AddToParser(parser)
    r_flags.GetVmCountFlag(False).AddToParser(parser)
    r_flags.GetReservationSharingPolicyFlag().AddToParser(parser)
    r_flags.GetEnableEmergentMaintenanceFlag().AddToParser(parser)
    r_flags.GetSharedSettingFlag(
        support_folder_share_setting=False).AddToParser(parser)
    r_flags.GetSchedulingTypeFlag().AddToParser(parser)

    auto_delete_group = base.ArgumentGroup(
        'Manage auto-delete properties for reservations.',
        required=False,
        mutex=True,
    )
    auto_delete_group.AddArgument(r_flags.GetDeleteAtTimeFlag())
    auto_delete_group.AddArgument(r_flags.GetDeleteAfterDurationFlag())
    auto_delete_group.AddArgument(r_flags.GetDisableAutoDelete())
    auto_delete_group.AddToParser(parser)


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(Update):
  """Update Compute Engine reservations."""

  _support_share_with_flag = True
  _support_auto_delete = True
  _support_reservation_sharing_policy = True
  _support_emergent_maintenance = True
  _support_share_type = True
  _support_scheduling_type = True

  @classmethod
  def Args(cls, parser):
    resource_args.GetReservationResourceArg().AddArgument(
        parser, operation_type='update'
    )
    r_flags.GetShareWithFlag().AddToParser(parser)
    r_flags.GetAddShareWithFlag().AddToParser(parser)
    r_flags.GetRemoveShareWithFlag().AddToParser(parser)
    r_flags.GetVmCountFlag(False).AddToParser(parser)
    r_flags.GetReservationSharingPolicyFlag().AddToParser(parser)
    r_flags.GetEnableEmergentMaintenanceFlag().AddToParser(parser)
    r_flags.GetSharedSettingFlag(
        support_folder_share_setting=False).AddToParser(parser)
    r_flags.GetSchedulingTypeFlag().AddToParser(parser)

    auto_delete_group = base.ArgumentGroup(
        'Manage auto-delete properties for reservations.',
        required=False,
        mutex=True,
    )
    auto_delete_group.AddArgument(r_flags.GetDeleteAtTimeFlag())
    auto_delete_group.AddArgument(r_flags.GetDeleteAfterDurationFlag())
    auto_delete_group.AddArgument(r_flags.GetDisableAutoDelete())
    auto_delete_group.AddToParser(parser)


Update.detailed_help = {
    'EXAMPLES':
        """
        To add `project-1,project-2,project-3` to the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --add-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To remove `project-1,project-2,project-3` from the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --remove-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To update the number of reserved VM instances to 500 for a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --zone=us-central1-a --vm-count=500
        """
}

UpdateBeta.detailed_help = {
    'EXAMPLES':
        """
        To add `project-1,project-2,project-3` to the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --add-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To remove `project-1,project-2,project-3` from the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --remove-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To update the entire list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --share-with=project-1,project-2,project-3 --zone=us-central1-a

        To update the number of reserved VM instances to 500 for a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --zone=us-central1-a --vm-count=500
        """
}

UpdateAlpha.detailed_help = {
    'EXAMPLES':
        """
        To add `project-1,project-2,project-3` to the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --add-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To remove `project-1,project-2,project-3` from the list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --remove-share-with=project-1,project-2,project-3 --zone=us-central1-a

        To update the entire list of projects that are shared with a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --share-with=project-1,project-2,project-3 --zone=us-central1-a

        To update the number of reserved VM instances to 500 for a Compute Engine reservation, `my-reservation` in zone: `us-central1-a`, run:

            $ {command} my-reservation --zone=us-central1-a --vm-count=500
        """
}
