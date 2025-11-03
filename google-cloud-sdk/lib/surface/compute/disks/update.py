# -*- coding: utf-8 -*- #
# Copyright 2017 Google LLC. All Rights Reserved.
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
"""Command for labels update to disks."""

import dataclasses
from typing import List

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import disks_util as api_util
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags
from googlecloudsdk.command_lib.util.args import labels_util
from googlecloudsdk.core import log

DETAILED_HELP = {
    'DESCRIPTION': '*{command}* updates a Compute Engine persistent disk.',
    'EXAMPLES': """\
        To update labels 'k0' and 'k1' and remove label 'k3' of a disk, run:

            $ {command} example-disk --zone=us-central1-a --update-labels=k0=value1,k1=value2 --remove-labels=k3

            ``k0'' and ``k1'' are added as new labels if not already present.

        Labels can be used to identify the disk. To list disks with the 'k1:value2' label, run:

            $ {parent_command} list --filter='labels.k1:value2'

        To list only the labels when describing a resource, use --format to filter the result:

            $ {parent_command} describe example-disk --format="default(labels)"

        To append licenses to the disk, run:

            $ {command} example-disk --zone=us-central1-a --append-licenses=projects/license-project/global/licenses/license-1,projects/license-project/global/licenses/license-2

        To remove licenses from the disk, run:

            $ {command} example-disk --zone=us-central1-a --replace-licenses=projects/license-project/global/licenses/license-1,projects/license-project/global/licenses/license-2

        To replace a license on the disk, run:

            $ {command} example-disk --zone=us-central1-a --replace-license=projects/license-project/global/licenses/old-license,projects/license-project/global/licenses/new-license
        """,
}


def _CommonArgs(
    messages,
    cls,
    parser,
    support_user_licenses=False,
    support_licenses=True,
    support_add_guest_os_features=False,
):
  """Add arguments used for parsing in all command tracks."""
  cls.DISK_ARG = disks_flags.MakeDiskArg(plural=False)
  cls.DISK_ARG.AddArgument(parser, operation_type='update')
  labels_util.AddUpdateLabelsFlags(parser)

  if support_user_licenses:
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument(
        '--update-user-licenses',
        type=arg_parsers.ArgList(),
        metavar='LICENSE',
        action=arg_parsers.UpdateAction,
        help=(
            'List of user licenses to be updated on a disk. These user licenses'
            ' will replace all existing user licenses. If this flag is not '
            'provided, all existing user licenses will remain unchanged.'))
    scope.add_argument(
        '--clear-user-licenses',
        action='store_true',
        help='Remove all existing user licenses on a disk.')

  if support_licenses:
    scope = parser.add_group()
    scope.add_argument(
        '--append-licenses',
        type=arg_parsers.ArgList(min_length=1),
        metavar='LICENSE',
        action=arg_parsers.UpdateAction,
        help=(
            '"A list of license URIs or license codes. These licenses will'
            ' be appended to the existing licenses on the disk. Provided'
            ' licenses can be either license URIs or license codes but'
            ' not a mix of both.'
        ),
    )
    scope.add_argument(
        '--remove-licenses',
        type=arg_parsers.ArgList(min_length=1),
        metavar='LICENSE',
        action=arg_parsers.UpdateAction,
        help=(
            'A list of license URIs or license codes. If'
            ' present in the set of existing licenses, these licenses will be'
            ' removed. If not present, this is a no-op. Provided licenses can'
            ' be either license URIs or license codes but not a mix of'
            ' both.'
        ),
    )
    scope.add_argument(
        '--replace-license',
        type=arg_parsers.ArgList(min_length=2, max_length=2),
        metavar='LICENSE',
        action=arg_parsers.UpdateAction,
        help=(
            'A list of license URIs or license codes. The first'
            ' license is the license to be replaced and the second license is'
            ' the replacement license. Provided licenses can be either'
            ' license URIs or license codes but not a mix of both.'
        ),
    )

  scope = parser.add_mutually_exclusive_group()

  architecture_enum_type = messages.Disk.ArchitectureValueValuesEnum
  excluded_enums = [architecture_enum_type.ARCHITECTURE_UNSPECIFIED.name]
  architecture_choices = sorted(
      [e for e in architecture_enum_type.names() if e not in excluded_enums])
  scope.add_argument(
      '--update-architecture',
      choices=architecture_choices,
      help=(
          'Updates the architecture or processor type that this disk '
          'can support. For available processor types on Compute Engine, '
          'see https://cloud.google.com/compute/docs/cpu-platforms.'
      ))
  scope.add_argument(
      '--clear-architecture',
      action='store_true',
      help=('Removes the architecture or processor '
            'type annotation from the disk.')
  )

  if support_add_guest_os_features:
    disks_flags.AddGuestOsFeatureArgs(parser, messages)

  disks_flags.AddAccessModeFlag(parser, messages)

  parser.add_argument(
      '--provisioned-iops',
      type=arg_parsers.BoundedInt(),
      help=(
          'Provisioned IOPS of disk to update. '
          'Only for use with disks of type '
          'hyperdisk-extreme.'
      ),
  )

  parser.add_argument('--provisioned-throughput',
                      type=arg_parsers.BoundedInt(),
                      help=(
                          'Provisioned throughput of disk to update. '
                          'The throughput unit is  MB per sec. '))

  parser.add_argument(
      '--size',
      type=arg_parsers.BinarySize(
          suggested_binary_size_scales=['GB', 'GiB', 'TB', 'TiB', 'PiB', 'PB']),
      help="""\
        Size of the disks. The value must be a whole
        number followed by a size unit of ``GB'' for gigabyte, or ``TB''
        for terabyte. If no size unit is specified, GB is
        assumed. For details about disk size limits, refer to:
        https://cloud.google.com/compute/docs/disks
        """)


def _LabelsFlagsIncluded(args):
  return args.IsSpecified('update_labels') or args.IsSpecified(
      'clear_labels') or args.IsSpecified('remove_labels')


def _UserLicensesFlagsIncluded(args):
  return args.IsSpecified('update_user_licenses') or args.IsSpecified(
      'clear_user_licenses')


def _LicensesFlagsIncluded(args):
  return (
      args.IsSpecified('append_licenses')
      or args.IsSpecified('remove_licenses')
      or args.IsSpecified('replace_license')
  )


def _ArchitectureFlagsIncluded(args):
  return args.IsSpecified('update_architecture') or args.IsSpecified(
      'clear_architecture')


def _AccessModeFlagsIncluded(args):
  return args.IsSpecified('access_mode')


def _ProvisionedIopsIncluded(args):
  return args.IsSpecified('provisioned_iops')


def _ProvisionedThroughputIncluded(args):
  return args.IsSpecified('provisioned_throughput')


def _SizeIncluded(args):
  return args.IsSpecified('size')


def _GuestOsFeatureFlagsIncluded(args):
  return args.IsKnownAndSpecified('add_guest_os_features')


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.GA)
class Update(base.UpdateCommand):
  r"""Update a Compute Engine persistent disk."""

  DISK_ARG = None

  @dataclasses.dataclass
  class LicenseUpdateData:
    update_via_license_code: bool
    licenses: List[str]
    license_codes: List[int]

  @classmethod
  def Args(cls, parser):
    messages = cls._GetApiHolder(no_http=True).client.messages
    _CommonArgs(
        messages, cls, parser, False)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def _isInt(self, license_code):
    try:
      int(license_code)
      return True
    except ValueError:
      return False

  def _UpdateRequiresDiskRead(self, args, support_licenses):
    return (
        support_licenses and _LicensesFlagsIncluded(args)
    ) or _GuestOsFeatureFlagsIncluded(args)

  def _VerifyLicenseArgsDoNotMixLicensesAndLicenseCodes(self, args):
    """Verifies that license args do not mix licenses and license codes.

    Args:
      args: The arguments that were provided by the user, which contains the
        license mutations.

    Raises:
      exceptions.InvalidArgumentException: If the user provided a mix of
      licenses and license codes.
    """

    all_licenses = []
    if args.IsSpecified('append_licenses'):
      all_licenses.extend(args.append_licenses)
    if args.IsSpecified('remove_licenses'):
      all_licenses.extend(args.remove_licenses)
    if args.IsSpecified('replace_license'):
      all_licenses.extend(args.replace_license)

    is_mixing_licenses_and_license_codes = any(
        self._isInt(license) for license in all_licenses
    ) and any(not self._isInt(license) for license in all_licenses)

    if is_mixing_licenses_and_license_codes:
      if args.IsSpecified('append_licenses'):
        raise exceptions.InvalidArgumentException(
            '--append-licenses',
            'Values must be either all license codes or all licenses, not a mix'
            ' of both.',
        )
      if args.IsSpecified('remove_licenses'):
        raise exceptions.InvalidArgumentException(
            '--remove-licenses',
            'Values must be either all license codes or all licenses, not a mix'
            ' of both.',
        )
      if args.IsSpecified('replace_license'):
        raise exceptions.InvalidArgumentException(
            '--replace-license',
            'Values must be either all license codes or all licenses, not a mix'
            ' of both.',
        )

  def _LicenseUpdateFormatIsCode(self, appended_licenses, removed_licenses):
    return all(self._isInt(license) for license in appended_licenses) and all(
        self._isInt(license) for license in removed_licenses
    )

  def _ParseLicenseCodesForUpdate(
      self, current_license_codes, appended_licenses, removed_licenses
  ):
    log.debug('Updating licenses via license codes')
    appended_licenses = [int(license) for license in appended_licenses]
    removed_licenses = [int(license) for license in removed_licenses]
    result_licenses = current_license_codes + appended_licenses
    for removed_license in removed_licenses:
      if removed_license in result_licenses:
        result_licenses.remove(removed_license)
    log.debug('License codes sent to api: ' + str(result_licenses))
    return result_licenses

  def _ParseLicensesForUpdate(
      self, holder, disk_ref, disk, appended_licenses, removed_licenses
  ):
    log.debug('Updating licenses via license names')
    # Parse input and existing licenses as relative paths for comparison.
    appended_licenses = [
        holder.resources.Parse(
            license,
            collection='compute.licenses',
            params={'project': disk_ref.project},
        ).RelativeName()
        for license in (disk.licenses + appended_licenses)
    ]
    log.debug(
        'appended_licenses & existing licenses: ' + str(appended_licenses)
    )
    removed_licenses = [
        holder.resources.Parse(
            license,
            collection='compute.licenses',
            params={'project': disk_ref.project},
        ).RelativeName()
        for license in removed_licenses
    ]
    log.debug('removed_licenses: ' + str(removed_licenses))
    for removed_license in removed_licenses:
      if removed_license in appended_licenses:
        appended_licenses.remove(removed_license)

    log.debug('Licenses sent to API: ' + str(appended_licenses))

    return appended_licenses

  def _ConstructLicenseUpdateData(self, args, holder, disk, disk_ref):
    appended_licenses = []
    removed_licenses = []
    if args.append_licenses:
      log.debug('Appending licenses: ' + str(args.append_licenses))
      appended_licenses = args.append_licenses
    if args.remove_licenses:
      log.debug('Removing licenses: ' + str(args.remove_licenses))
      removed_licenses = args.remove_licenses
    if args.replace_license:
      log.debug(
          'Replacing license '
          + str(args.replace_license[0])
          + ' with '
          + str(args.replace_license[1])
      )
      appended_licenses.append(args.replace_license[1])
      removed_licenses.append(args.replace_license[0])
    if self._LicenseUpdateFormatIsCode(appended_licenses, removed_licenses):
      license_codes = self._ParseLicenseCodesForUpdate(
          disk.licenseCodes, appended_licenses, removed_licenses
      )
      return self.LicenseUpdateData(
          update_via_license_code=True,
          licenses=[],
          license_codes=license_codes,
      )
    else:
      license_names = self._ParseLicensesForUpdate(
          holder, disk_ref, disk, appended_licenses, removed_licenses
      )
      return self.LicenseUpdateData(
          update_via_license_code=False,
          licenses=license_names,
          license_codes=[],
      )

  def Run(self, args):
    return self._Run(
        args,
        support_user_licenses=False,
        support_licenses=True,
    )

  def _Run(
      self,
      args,
      support_user_licenses=False,
      support_licenses=True,
  ):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client.apitools_client
    messages = holder.client.messages

    disk_ref = self.DISK_ARG.ResolveAsResource(
        args, holder.resources,
        scope_lister=flags.GetDefaultScopeLister(holder.client))
    disk_info = api_util.GetDiskInfo(disk_ref, client, messages)
    service = disk_info.GetService()

    if (
        _ProvisionedIopsIncluded(args)
        or _ProvisionedThroughputIncluded(args)
        or _ArchitectureFlagsIncluded(args)
        or _SizeIncluded(args)
        or (support_user_licenses and _UserLicensesFlagsIncluded(args))
        or (support_licenses and _LicensesFlagsIncluded(args))
        or _AccessModeFlagsIncluded(args)
        or _GuestOsFeatureFlagsIncluded(args)
    ):
      disk_res = messages.Disk(name=disk_ref.Name())
      disk_update_request = None
      if disk_ref.Collection() == 'compute.disks':
        disk_update_request = messages.ComputeDisksUpdateRequest(
            project=disk_ref.project,
            disk=disk_ref.Name(),
            diskResource=disk_res,
            zone=disk_ref.zone,
            paths=[])
      else:
        disk_update_request = messages.ComputeRegionDisksUpdateRequest(
            project=disk_ref.project,
            disk=disk_ref.Name(),
            diskResource=disk_res,
            region=disk_ref.region,
            paths=[])

      # Some updates require the current state of the disk.
      disk = None
      if self._UpdateRequiresDiskRead(args, support_licenses):
        disk = disk_info.GetDiskResource()

      if support_user_licenses and _UserLicensesFlagsIncluded(args):
        if args.update_user_licenses:
          disk_res.userLicenses = args.update_user_licenses
        disk_update_request.paths.append('userLicenses')

      if support_licenses and _LicensesFlagsIncluded(args):
        self._VerifyLicenseArgsDoNotMixLicensesAndLicenseCodes(args)
        license_update_data = self._ConstructLicenseUpdateData(
            args, holder, disk, disk_ref
        )
        if license_update_data.update_via_license_code:
          disk_res.licenseCodes = license_update_data.license_codes
          disk_update_request.paths.append('licenseCodes')
        else:
          disk_res.licenses = license_update_data.licenses
          disk_update_request.paths.append('licenses')

      if _ArchitectureFlagsIncluded(args):
        if args.update_architecture:
          disk_res.architecture = disk_res.ArchitectureValueValuesEnum(
              args.update_architecture)
        disk_update_request.paths.append('architecture')

      if _AccessModeFlagsIncluded(args):
        disk_res.accessMode = disk_res.AccessModeValueValuesEnum(
            args.access_mode
        )
        disk_update_request.paths.append('accessMode')

      if _ProvisionedIopsIncluded(args):
        if args.provisioned_iops:
          disk_res.provisionedIops = args.provisioned_iops
          disk_update_request.paths.append('provisionedIops')

      if _ProvisionedThroughputIncluded(
          args):
        if args.provisioned_throughput:
          disk_res.provisionedThroughput = args.provisioned_throughput
          disk_update_request.paths.append('provisionedThroughput')

      if _SizeIncluded(args) and args.size:
        disk_res.sizeGb = utils.BytesToGb(args.size)
        disk_update_request.paths.append('sizeGb')

      if _GuestOsFeatureFlagsIncluded(args):
        if args.add_guest_os_features:
          disk_res.guestOsFeatures = [
              messages.GuestOsFeature(
                  type=messages.GuestOsFeature.TypeValueValuesEnum(
                      args.add_guest_os_features
                  )
              )
          ] + disk.guestOsFeatures
          disk_update_request.paths.append('guestOsFeatures')

      update_operation = service.Update(disk_update_request)
      update_operation_ref = holder.resources.Parse(
          update_operation.selfLink,
          collection=disk_info.GetOperationCollection())
      update_operation_poller = poller.Poller(service)
      result = waiter.WaitFor(
          update_operation_poller, update_operation_ref,
          'Updating fields of disk [{0}]'.format(disk_ref.Name()))
      if not _LabelsFlagsIncluded(args):
        return result

    labels_diff = labels_util.GetAndValidateOpsFromArgs(args)

    disk = disk_info.GetDiskResource()

    set_label_req = disk_info.GetSetLabelsRequestMessage()
    labels_update = labels_diff.Apply(set_label_req.LabelsValue, disk.labels)
    request = disk_info.GetSetDiskLabelsRequestMessage(
        disk, labels_update.GetOrNone())

    if not labels_update.needs_update:
      return disk

    operation = service.SetLabels(request)
    operation_ref = holder.resources.Parse(
        operation.selfLink, collection=disk_info.GetOperationCollection())

    operation_poller = poller.Poller(service)
    return waiter.WaitFor(
        operation_poller, operation_ref,
        'Updating labels of disk [{0}]'.format(
            disk_ref.Name()))


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(Update):
  r"""Update a Compute Engine persistent disk."""

  DISK_ARG = None

  @classmethod
  def Args(cls, parser):
    messages = cls._GetApiHolder(no_http=True).client.messages
    _CommonArgs(
        messages, cls, parser, support_user_licenses=True)

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args):
    return self._Run(
        args,
        support_user_licenses=True,
        support_licenses=True)


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class UpdateAlpha(UpdateBeta):
  r"""Update a Compute Engine persistent disk."""

  DISK_ARG = None

  @classmethod
  def Args(cls, parser):
    messages = cls._GetApiHolder(no_http=True).client.messages
    _CommonArgs(
        messages,
        cls,
        parser,
        support_user_licenses=True,
        support_licenses=True,
        support_add_guest_os_features=True,
    )

  @classmethod
  def _GetApiHolder(cls, no_http=False):
    return base_classes.ComputeApiHolder(cls.ReleaseTrack(), no_http)

  def Run(self, args):
    return self._Run(args, support_user_licenses=True, support_licenses=True)


Update.detailed_help = DETAILED_HELP

UpdateBeta.detailed_help = Update.detailed_help

UpdateAlpha.detailed_help = UpdateBeta.detailed_help
