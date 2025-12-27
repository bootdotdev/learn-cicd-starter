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
"""The command group for Disk Migrations."""

from googlecloudsdk.calliope import base


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class DiskMigrations(base.Group):
  r"""Migrates disks to Compute Engine.

  The gcloud alpha migration vms disk-migrations command lets you create and
  manage disk migration resource. You must create a disk migration resource
  before you can migrate your disk from any migration source to a Compute Engine
  disk. The disk migration resource tracks the progress of the disk migration.
  To use this command, you must enable VM Migration API in your project.

  Note that this command only creates a disk migration resource. It does not
  initiate the disk migration process. After creating the disk migration
  resource, you must initiate the migration process using the run command.


  The disk is migrated to a Google Cloud Project, designated by the Target Project resource.
  To get a list of Target Projects, run the gcloud alpha migration vms target-projects list command.
  For information on adding target projects, see https://cloud.google.com/migrate/virtual-machines/docs/5.0/how-to/target-project.

  A project can support a maximum of 200 Disk/VM Migration active resources per project; 1000 ready disk migration resources, and 500 finished disk migration resources.
  Hence we recommend that you delete a completed disk migrations to avoid reaching the disk migration resources limit.
  Deletion of disk migration resource does not affect the migrated disk.

  ## Create Disk Migration
  $ gcloud migration vms disk-migrations create DISK_MIGRATION_JOB_NAME \
    --source=AWS_SOURCE_NAME \
    --source-volume-id=AWS_VOLUME_ID \
    --location=REGION \
    --target-project=TARGET_PROJECT_RESOURCE_PATH

  ## Run Disk Migration
  $ gcloud migration vms disk-migrations run DISK_MIGRATION_JOB_NAME \
    --source=AWS_SOURCE_NAME \
    --location=REGION \

  ## Delete Disk Migration resource
  $ gcloud migration vms disk-migrations delete DISK_MIGRATION_JOB_NAME \
    --location=REGION
  """
