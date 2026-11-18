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
"""Command to get capacity advice for Compute Engine resources."""

import collections
import re

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import utils
from googlecloudsdk.calliope import arg_parsers
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions
from googlecloudsdk.command_lib.compute import completers
from googlecloudsdk.command_lib.compute.advice import flags
from googlecloudsdk.core import properties


DETAILED_HELP = {
    "DESCRIPTION": """
      Get capacity advice for Compute Engine resources.

      This command helps you view future resource availability for a specific
      number of VM instances, machine type, provisioning model, and zone. After
      you confirm resource availability, you can specify those configurations
      when you create VM instances. This action improves the success rate of
      your VM instance creation request.
    """,
    "EXAMPLES": """
      To check the availability of 100 `n2-standard-32` Spot VMs in any single
      zone in the `us-central1` region, run the following command:

        $ {command} \
            --region="us-central1" \
            --provisioning-model="SPOT" \
            --size=100 \
            --instance-selection-machine-types="n2-standard-32" \
            --target-distribution-shape="any-single-zone"

      To check the availability of 50 Spot VMs, allowing either `e2-standard-8`
      or `e2-standard-16` machine types, distributed across `us-central1-a` and
      `us-central1-b`, run the following command:

        $ {command} \
            --region="us-central1" \
            --provisioning-model="SPOT" \
            --size=50 \
            --instance-selection="name=my-selection,machine-type=e2-standard-8,machine-type=e2-standard-16" \
            --target-distribution-shape="any" \
            --zones="us-central1-a,us-central1-b"
      """,
}


class ArgMultiValueDict:
  """Converts argument values into multi-valued mappings.

  Values for repeated keys are collected in a list. Ensures all values are
  key-value pairs and handles invalid cases.
  """

  def __init__(self):
    ops = "="
    key_op_value_pattern = r"([^\s{ops}]+)\s*{ops}\s*(.*)".format(ops=ops)
    self._key_op_value = re.compile(key_op_value_pattern, re.DOTALL)

  def __call__(self, arg_value):
    arg_list = [item.strip() for item in arg_value.split(",")]
    arg_dict = collections.OrderedDict()
    for arg in arg_list:
      # Enforce key-value pair structure
      if "=" not in arg:
        raise arg_parsers.ArgumentTypeError(
            "Invalid flag value [{0}]".format(arg)
        )
      match = self._key_op_value.match(arg)
      if not match:
        raise arg_parsers.ArgumentTypeError(
            "Invalid flag value [{0}]".format(arg)
        )
      key, value = match.group(1).strip(), match.group(2).strip()
      if not key or not value:
        raise arg_parsers.ArgumentTypeError(
            "Invalid flag value [{0}]".format(arg)
        )
      # Prevent values from containing '='
      if "=" in value:
        raise arg_parsers.ArgumentTypeError(
            "Invalid flag value [{0}]".format(arg)
        )
      arg_dict.setdefault(key, []).append(value)

    return arg_dict


@base.DefaultUniverseOnly
@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
@base.Hidden
class Capacity(base.Command):
  """Get capacity advice for Compute Engine resources."""

  detailed_help = DETAILED_HELP
  category = base.COMPUTE_CATEGORY

  @staticmethod
  def Args(parser):
    """Registers flags for this command."""
    flags.AddRegionFlag(parser)
    flags.AddProvisioningModelFlag(parser)
    parser.add_argument(
        "--size",
        type=int,
        required=True,
        help="The total number of VMs being requested in the capacity query.",
    )

    instance_selection_group = parser.add_group(
        required=True,
        help="Specifies the machine types for which advice is being sought.",
    )
    instance_selection_group.add_argument(
        "--instance-selection-machine-types",
        type=arg_parsers.ArgList(),
        metavar="MACHINE_TYPE",
        help="Specifies a comma-separated list of preferred machine types for "
        "creating virtual machines.",
    )
    instance_selection_group.add_argument(
        "--instance-selection",
        help='Named selection of machine types. For '
        'example, --instance-selection="name=instance-selection-1,'
        'machine-type=e2-standard-8,machine-type=t2d-standard-8".',
        metavar="INSTANCE_SELECTION",
        type=ArgMultiValueDict(),
    )

    flags.AddTargetDistributionShapeFlag(parser)
    parser.add_argument(
        "--zones",
        type=arg_parsers.ArgList(),
        completer=completers.ZonesCompleter,
        metavar="ZONE",
        required=False,
        help=(
            "A comma-separated list of zones to query within the specified"
            " region, for example, `us-central1-a,us-central1-b`. If you omit"
            " this flag, then you view availability for your requested capacity"
            " across all zones in the region."
        ),
    )

  def Run(self, args):
    """Runs the capacity advice command."""
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client
    messages = client.messages
    flags.ValidateZonesAndRegionFlags(args, holder.resources)
    if args.instance_selection and not args.instance_selection.get(
        "machine-type"
    ):
      raise exceptions.InvalidArgumentException(
          "--instance-selection",
          "At least one 'machine-type' must be specified.",
      )

    project = properties.VALUES.core.project.GetOrFail()
    region = args.region
    if not region and args.zones:
      # All zones are in the same region, this is validated in
      # ValidateZonesAndRegionFlags.
      region = utils.ZoneNameToRegionName(args.zones[0])

    region = region or properties.VALUES.compute.region.Get()
    if not region:
      raise exceptions.RequiredArgumentException(
          "--region", "The [compute/region] property must be set.")

    # Instance Properties
    scheduling = messages.CapacityAdviceRequestInstancePropertiesScheduling(
        provisioningModel=messages.CapacityAdviceRequestInstancePropertiesScheduling.ProvisioningModelValueValuesEnum(
            args.provisioning_model
        )
    )
    instance_properties = messages.CapacityAdviceRequestInstanceProperties(
        scheduling=scheduling)

    # Distribution Policy
    target_shape = None
    if args.IsSpecified("target_distribution_shape"):
      target_shape = (
          messages.CapacityAdviceRequestDistributionPolicy.TargetShapeValueValuesEnum(
              args.target_distribution_shape)
      )
    zone_configs = None
    if args.zones:
      zone_configs = []
      for zone in args.zones:
        zone_ref = holder.resources.Parse(
            zone,
            params={"project": project},
            collection="compute.zones")
        zone_configs.append(
            messages.CapacityAdviceRequestDistributionPolicyZoneConfiguration(
                zone=zone_ref.SelfLink()))
    distribution_policy = messages.CapacityAdviceRequestDistributionPolicy(
        targetShape=target_shape)
    if zone_configs:
      distribution_policy.zones = zone_configs
    selections_map = {}
    default_instance_selection_name = "instance-selection-1"
    if args.instance_selection:
      selection_name_list = args.instance_selection.get("name")
      selection_name = (
          selection_name_list[0]
          if selection_name_list
          else default_instance_selection_name
      )
      selections_map[selection_name] = (
          messages.CapacityAdviceRequestInstanceFlexibilityPolicyInstanceSelection(
              machineTypes=args.instance_selection.get("machine-type"),
          )
      )
    elif args.instance_selection_machine_types:
      selections_map[default_instance_selection_name] = (
          messages.CapacityAdviceRequestInstanceFlexibilityPolicyInstanceSelection(
              machineTypes=args.instance_selection_machine_types,
          )
      )

    additional_properties = []
    for key, value in selections_map.items():
      additional_properties.append(
          messages.CapacityAdviceRequestInstanceFlexibilityPolicy.InstanceSelectionsValue.AdditionalProperty(
              key=key, value=value)
      )

    instance_selections_value = (
        messages.CapacityAdviceRequestInstanceFlexibilityPolicy.InstanceSelectionsValue(
            additionalProperties=additional_properties
        )
    )
    instance_flexibility_policy = (
        messages.CapacityAdviceRequestInstanceFlexibilityPolicy(
            instanceSelections=instance_selections_value
        )
    )

    inner_request = messages.CapacityAdviceRequest(
        distributionPolicy=distribution_policy,
        instanceFlexibilityPolicy=instance_flexibility_policy,
        instanceProperties=instance_properties,
        size=args.size,
    )

    outer_request = messages.ComputeAdviceCapacityRequest(
        project=project,
        region=region,
        capacityAdviceRequest=inner_request,
    )

    return client.apitools_client.advice.Capacity(outer_request)
