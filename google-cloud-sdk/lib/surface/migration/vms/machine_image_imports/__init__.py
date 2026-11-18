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
"""The command group for Machine Image Imports."""

from googlecloudsdk.calliope import base


@base.ReleaseTracks(base.ReleaseTrack.GA, base.ReleaseTrack.ALPHA)
@base.DefaultUniverseOnly
class MachineImageImports(base.Group):
  r"""Imports machine images to Google Compute Engine from Google Cloud Storage.

  gcloud migration vms machine-image-imports provides a more robust and better
  supported method for importing machine images to Google Compute Engine.
  Other image-related operations (for example, list) can be done using
  gcloud compute images, as usual.

  The commands use VM Migration API which supports importing of a machine image from
  a Google Cloud Storage file (gs://...) to a target project.
  VM Migration API must be enabled in your project.

  `gcloud migration vms machine-image-imports create` creates a machine Image Import resource
  with a nested Image Import Job resource. The Image Import Job resource tracks
  the machine image import progress. After the Image Import Job completes, successfully
  or otherwise, there's no further use for the Image Import resource.

  The machine image is imported to a Google Cloud Project, desginated by the
  Target Project resource. To get a list of Target Projects, run the
  gcloud alpha migration vms target-projects list command.
  Use the Google Cloud console to add target project resources.
  For information on adding target projects, see
  https://cloud.google.com/migrate/virtual-machines/docs/5.0/how-to/target-project.

  A project can support up to a certain number of Image Import resources per project.
  Hence it's recommended to delete an Image Import resource after the Image
  Import Job is complete to avoid reaching the Image Import resources limit.
  Deletion of Image Import resource does not affect the imported machine image.
  For more information about the image import resource, see
  https://cloud.google.com/migrate/virtual-machines/docs/5.0/migrate/image_import.

  ## Import Image
  $ gcloud migration vms machine-image-imports create MACHINE_IMAGE_IMPORT_NAME \
    --source-file=GCS_FILE_NAME \
    --image-name=IMPORTED_IMAGE_NAME \
    --location=REGION \
    --target-project=TARGET_PROJECT_RESOURCE_PATH

  ## Delete Image Import resource
  $ gcloud migration vms machine-image-imports delete MACHINE_IMAGE_IMPORT_NAME \
    --location=REGION
  """
