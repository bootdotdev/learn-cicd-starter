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
"""Command for converting a disk to a different type."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import enum
import textwrap

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import disks_util
from googlecloudsdk.api_lib.compute import kms_utils
from googlecloudsdk.api_lib.compute import name_generator
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import completers
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.disks import flags as disks_flags
from googlecloudsdk.command_lib.kms import resource_args as kms_resource_args
from googlecloudsdk.core import exceptions as core_exceptions
from googlecloudsdk.core import log
from googlecloudsdk.core.console import console_io
from googlecloudsdk.core.console import progress_tracker


CONTINUE_WITH_CONVERT_PROMPT = (
    'This command will permanently convert disk {0} to disk type: {1}. Please'
    ' detach the disk from all instances before continuing. Data written to the'
    ' original disk during conversion will not appear on the converted disk.'
    ' Please see'
    ' https://cloud.google.com/compute/docs/disks/automatically-convert-disks'
    ' for more details.'
)


class _ConvertState(enum.Enum):
  SNAPSHOT_CREATED = 1
  DISK_RESTORED = 2
  ORIGINAL_DISK_DELETED = 3
  ORIGINAL_DISK_RECREATED = 4
  RESTORED_DISK_DELETED = 5
  SNAPSHOT_DELETED = 6


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA,
                    base.ReleaseTrack.BETA,
                    base.ReleaseTrack.GA)
class Convert(base.RestoreCommand):
  """Convert a Compute Engine Persistent Disk volume to a Hyperdisk volume."""

  _DISK_ARG = disks_flags.MakeDiskArg(plural=False)

  @staticmethod
  def Args(parser):
    Convert._DISK_ARG.AddArgument(parser)
    parser.add_argument(
        '--target-disk-type',
        completer=completers.DiskTypesCompleter,
        required=True,
        help="""Specifies the type of Hyperdisk to convert to, for example,
        to convert a Hyperdisk Balanced volume, specify `hyperdisk-balanced`. To get a
        list of available disk types, run `gcloud compute disk-types list`.
        """,
    )
    kms_resource_args.AddKmsKeyResourceArg(
        parser, 'disk', region_fallthrough=True
    )

  def Run(self, args):
    self.holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    self.client = self.holder.client.apitools_client
    self.messages = self.holder.client.messages
    self.state = None
    self.created_resources = {}
    self.user_messages = ''

    self.disk_ref = self._DISK_ARG.ResolveAsResource(
        args,
        self.holder.resources,
        scope_lister=flags.GetDefaultScopeLister(self.holder.client),
    )

    if self.disk_ref.Collection() == 'compute.regionDisks':
      raise exceptions.InvalidArgumentException(
          '--region',
          'Regional disks are not supported for this command.'
      )

    if args.target_disk_type == 'hyperdisk-ml':
      raise exceptions.InvalidArgumentException(
          '--target-disk-type',
          'Hyperdisk ML is not supported for this command.',
      )
    self.target_disk_type = args.target_disk_type

    # make sure disk is not attached to any instances
    disk_info = disks_util.GetDiskInfo(
        self.disk_ref, self.client, self.messages)
    original_disk = disk_info.GetDiskResource()
    if original_disk.users:
      raise exceptions.ToolException(
          'Disk is attached to instances. Please detach the disk before'
          ' converting.'
      )
    console_io.PromptContinue(
        message=textwrap.dedent(
            CONTINUE_WITH_CONVERT_PROMPT.format(
                self.disk_ref.Name(), self.target_disk_type
            )
        ),
        cancel_on_no=True,
    )

    try:
      with self._CreateProgressTracker(self.disk_ref.Name()):
        result = self._ConvertDisk(
            self.disk_ref, self.target_disk_type, original_disk.sizeGb,
            disk_encryption_key=kms_utils.MaybeGetKmsKey(
                args, self.messages, None
            ),
        )
    except Exception as e:
      raise e
    finally:
      self._CleanUp()
      if self.user_messages:
        if self.state in [_ConvertState.ORIGINAL_DISK_RECREATED,
                          _ConvertState.RESTORED_DISK_DELETED,
                          _ConvertState.SNAPSHOT_DELETED]:
          log.warning(self.user_messages)
        else:
          log.error(self.user_messages)

    return result

  def _ConvertDisk(
      self, disk_ref, target_disk_type, size_gb, disk_encryption_key=None
  ):
    # create a snapshot of the disk
    self.snapshot_name = self._GenerateName(disk_ref)
    result = self._InsertSnapshot(disk_ref, self.snapshot_name)
    snapshot_ref = self.holder.resources.Parse(
        self.snapshot_name,
        params={'project': disk_ref.project},
        collection='compute.snapshots',
    )
    self._UpdateState(_ConvertState.SNAPSHOT_CREATED, snapshot_ref)
    # create a new disk from the snapshot with target disk type
    self.restored_disk_name = self._GenerateName(disk_ref)
    restored_disk_ref = self.holder.resources.Parse(
        self.restored_disk_name,
        params={'project': disk_ref.project, 'zone': disk_ref.zone},
        collection='compute.disks',
    )
    result = (
        self._RestoreDiskFromSnapshot(
            restored_disk_ref,
            snapshot_ref,
            target_disk_type,
            size_gb,
            disk_encryption_key=disk_encryption_key,
        )
        or result
    )
    self._UpdateState(_ConvertState.DISK_RESTORED, restored_disk_ref)
    # delete the original disk
    result = self._DeleteDisk(disk_ref) or result
    self._UpdateState(_ConvertState.ORIGINAL_DISK_DELETED)

    # recreate the original disk with the new disk as source
    result = (
        self._CloneDisk(
            disk_ref.Name(),
            restored_disk_ref,
            disk_encryption_key=disk_encryption_key,
        )
        or result
    )
    self._UpdateState(_ConvertState.ORIGINAL_DISK_RECREATED)

    # delete the restored disk because the original disk is recreated
    result = self._DeleteDisk(restored_disk_ref) or result
    self._UpdateState(_ConvertState.RESTORED_DISK_DELETED)

    # delete the snapshot because the disk is recreated
    result = self._DeleteSnapshot(snapshot_ref) or result
    self._UpdateState(_ConvertState.SNAPSHOT_DELETED)

    return result

  def _InsertSnapshot(self, disk_ref, snapshot_name):
    request = self.messages.ComputeSnapshotsInsertRequest(
        project=disk_ref.project,
        snapshot=self.messages.Snapshot(
            name=snapshot_name,
            sourceDisk=disk_ref.SelfLink(),
            snapshotType=self.messages.Snapshot.SnapshotTypeValueValuesEnum.STANDARD,
        ),
    )
    operation = self._MakeRequest(self.client.snapshots, 'Insert', request)
    operation_ref = self.holder.resources.Parse(
        operation.selfLink,
        collection='compute.globalOperations',
    )
    return waiter.WaitFor(
        poller.Poller(self.client.snapshots),
        operation_ref,
        custom_tracker=self._CreateNoOpProgressTracker(),
        max_wait_ms=None,
    )

  def _DeleteSnapshot(self, snapshot_ref):
    request = self.messages.ComputeSnapshotsDeleteRequest(
        snapshot=snapshot_ref.Name(),
        project=snapshot_ref.project,
    )
    operation = self._MakeRequest(self.client.snapshots, 'Delete', request)
    operation_ref = self.holder.resources.Parse(
        operation.selfLink,
        collection='compute.globalOperations',
    )
    return waiter.WaitFor(
        poller.DeletePoller(self.client.snapshots),
        operation_ref,
        custom_tracker=self._CreateNoOpProgressTracker(),
        max_wait_ms=None,
    )

  def _RestoreDiskFromSnapshot(
      self,
      restored_disk_ref,
      snapshot_ref,
      disk_type,
      size_gb,
      disk_encryption_key=None,
  ):
    kwargs = {}
    if disk_encryption_key:
      kwargs['diskEncryptionKey'] = disk_encryption_key
    disk = self.messages.Disk(
        name=restored_disk_ref.Name(),
        type=disks_util.GetDiskTypeUri(
            disk_type, restored_disk_ref, self.holder
        ),
        sizeGb=size_gb,
        sourceSnapshot=snapshot_ref.SelfLink(),
        **kwargs,
    )

    request = self.messages.ComputeDisksInsertRequest(
        disk=disk,
        project=restored_disk_ref.project,
        zone=restored_disk_ref.zone,
    )
    operation = self._MakeRequest(self.client.disks, 'Insert', request)
    operation_ref = self.holder.resources.Parse(
        operation.selfLink,
        collection='compute.zoneOperations',
    )
    return waiter.WaitFor(
        poller.Poller(self.client.disks),
        operation_ref,
        custom_tracker=self._CreateNoOpProgressTracker(),
        max_wait_ms=None,
    )

  def _GenerateName(self, resource_ref):
    return f'{name_generator.GenerateRandomName()}-{resource_ref.Name()}'[:64]

  def _DeleteDisk(self, disk_ref):
    request = self.messages.ComputeDisksDeleteRequest(
        disk=disk_ref.Name(),
        project=disk_ref.project,
        zone=disk_ref.zone,
    )
    operation = self._MakeRequest(self.client.disks, 'Delete', request)
    operation_ref = self.holder.resources.Parse(
        operation.selfLink,
        collection='compute.zoneOperations',
    )
    return waiter.WaitFor(
        poller.DeletePoller(self.client.disks),
        operation_ref,
        custom_tracker=self._CreateNoOpProgressTracker(),
        max_wait_ms=None,
    )

  def _CloneDisk(
      self, original_disk_name, restored_disk_ref, disk_encryption_key=None
  ):
    kwargs = {}
    if disk_encryption_key:
      kwargs['diskEncryptionKey'] = disk_encryption_key
    disk = self.messages.Disk(
        name=original_disk_name,
        sourceDisk=restored_disk_ref.SelfLink(),
        **kwargs,
    )
    request = self.messages.ComputeDisksInsertRequest(
        disk=disk,
        project=restored_disk_ref.project,
        zone=restored_disk_ref.zone,
    )
    operation = self._MakeRequest(self.client.disks, 'Insert', request)
    operation_ref = self.holder.resources.Parse(
        operation.selfLink,
        collection='compute.zoneOperations',
    )
    operation_poller = poller.Poller(self.client.disks)
    return waiter.WaitFor(
        operation_poller,
        operation_ref,
        custom_tracker=self._CreateNoOpProgressTracker(),
        max_wait_ms=None,
    )

  def _MakeRequest(self, resource_client, method, request):
    errors_to_collect = []
    responses = self.holder.client.AsyncRequests(
        [(resource_client, method, request)], errors_to_collect
    )
    if errors_to_collect:
      raise core_exceptions.MultiError(errors_to_collect)
    if not responses:
      raise core_exceptions.InternalError('No response received')
    return responses[0]

  def _UpdateState(self, state, created_resource=None):
    self.state = state
    if created_resource:
      self.created_resources[state] = created_resource

  def _CleanUp(self):
    if not self.state:
      self.user_messages = (
          'Creating snapshot failed.' + self._BuildCleanupSnapshotMessage()
      )
      return
    if self.state == _ConvertState.SNAPSHOT_CREATED:
      # restore disk failed
      self.user_messages = (
          f'Creating disk from snapshot {self.snapshot_name} failed. '
          + self._BuildCleanupSnapshotMessage()
      )
      self._DeleteSnapshot(
          self.created_resources[_ConvertState.SNAPSHOT_CREATED]
      )
    elif self.state == _ConvertState.DISK_RESTORED:
      # delete original disk request failed
      self.user_messages = (
          f'Deleting original disk {self.disk_ref.Name()} failed. '
          + self._BuildCleanupDiskMessage()
          + self._BuildCleanupSnapshotMessage()
      )
      self._DeleteDisk(self.created_resources[_ConvertState.DISK_RESTORED])
      self._DeleteSnapshot(
          self.created_resources[_ConvertState.SNAPSHOT_CREATED]
      )
    elif self.state == _ConvertState.ORIGINAL_DISK_DELETED:
      # recreate original disk failed
      self.user_messages = (
          f'Recreating original disk {self.disk_ref.Name()} failed. Please run'
          ' `gcloud compute disks create'
          f' {self.disk_ref.Name()} --zone={self.disk_ref.zone} --type={self.target_disk_type} --source-disk={self.restored_disk_name}`'
          ' to recreate the original disk. Please run `gcloud compute'
          f' snapshots delete {self.snapshot_name}` to delete the temporary'
          ' snapshot. Please run `gcloud compute disks delete'
          f' {self.restored_disk_name} --zone={self.disk_ref.zone}` to delete'
          ' the temporary disk.'
      )
    elif self.state == _ConvertState.ORIGINAL_DISK_RECREATED:
      # delete restored disk failed
      self.user_messages = (
          'Conversion completed successfully, Deleting temporary disk'
          f' {self.restored_disk_name} failed.'
          + self._BuildCleanupDiskMessage()
          + self._BuildCleanupSnapshotMessage()
      )
    elif self.state == _ConvertState.RESTORED_DISK_DELETED:
      self.user_messages = (
          'Conversion completed successfully. Deleting temporary snapshot'
          f' {self.snapshot_name} failed.'
          + self._BuildCleanupSnapshotMessage()
      )

  def _CreateProgressTracker(self, disk_name):
    return progress_tracker.ProgressTracker(
        message=f'Converting disk {disk_name}...',
        aborted_message='Conversion aborted.',
    )

  def _CreateNoOpProgressTracker(self):
    return progress_tracker.NoOpProgressTracker(
        interruptable=True, aborted_message=''
    )

  def _BuildCleanupSnapshotMessage(self):
    return (
        f' Please run `gcloud compute snapshots delete {self.snapshot_name}` to'
        ' delete the temporary snapshot if it still exists.'
    )

  def _BuildCleanupDiskMessage(self):
    return (
        ' Please run `gcloud compute disks delete'
        f' {self.restored_disk_name} --zone={self.disk_ref.zone}` to delete the'
        ' temporary disk if it still exists.'
    )


Convert.detailed_help = {
    'DESCRIPTION': """\
 Convert Compute Engine Persistent Disk volumes to Hyperdisk volumes.

 *{command}* converts a Compute Engine Persistent Disk volume to a Hyperdisk volume. For a comprehensive guide, refer to: https://cloud.google.com/sdk/gcloud/reference/compute/disks/convert.
    """,
    'EXAMPLES': """\
The following command converts a Persistent Disk volume to a Hyperdisk Balanced volume:

        $ {command} my-disk-1 --zone=ZONE --target-disk-type=hyperdisk-balanced
        """,
}
