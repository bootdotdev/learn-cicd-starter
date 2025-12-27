# -*- coding: utf-8 -*- #
# Copyright 2019 Google LLC. All Rights Reserved.
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
"""Create public delegated prefix command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import public_delegated_prefixes
from googlecloudsdk.api_lib.compute import utils as compute_api
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags as compute_flags
from googlecloudsdk.command_lib.compute.public_delegated_prefixes import flags
from googlecloudsdk.command_lib.util.apis import arg_utils
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.GA)
@base.UniverseCompatible
class Create(base.CreateCommand):
  r"""Creates a Compute Engine public delegated prefix.

  ## EXAMPLES

  To create a public delegated prefix:

    $ {command} my-public-delegated-prefix --public-advertised-prefix=my-pap \
      --range=120.120.10.128/27 --global
  """

  _api_version = compute_api.COMPUTE_GA_API_VERSION
  _include_internal_subnetwork_creation_mode = False

  @classmethod
  def Args(cls, parser):
    flags.MakePublicDelegatedPrefixesArg().AddArgument(parser)
    flags.AddCreatePdpArgsToParser(
        parser, cls._include_internal_subnetwork_creation_mode
    )

  def _Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    pdp_client = public_delegated_prefixes.PublicDelegatedPrefixesClient(
        holder.client, holder.client.messages, holder.resources
    )
    pdp_ref = flags.MakePublicDelegatedPrefixesArg().ResolveAsResource(
        args,
        holder.resources,
        scope_lister=compute_flags.GetDefaultScopeLister(holder.client),
    )

    if args.mode:
      input_mode = arg_utils.ChoiceToEnum(
          args.mode,
          holder.client.messages.PublicDelegatedPrefix.ModeValueValuesEnum,
      )
    else:
      input_mode = None

    if hasattr(args, 'purpose') and args.purpose:
      purpose = arg_utils.ChoiceToEnum(
          args.purpose,
          holder.client.messages.PublicDelegatedPrefix.PurposeValueValuesEnum,
      )
    else:
      purpose = None

    result = pdp_client.Create(
        pdp_ref,
        parent_pap_prefix=args.public_advertised_prefix
        if args.public_advertised_prefix
        else None,
        parent_pdp_prefix=args.public_delegated_prefix
        if args.public_delegated_prefix
        else None,
        ip_cidr_range=args.range,
        description=args.description,
        enable_live_migration=args.enable_live_migration,
        mode=input_mode,
        allocatable_prefix_length=int(args.allocatable_prefix_length)
        if args.allocatable_prefix_length
        else None,
        purpose=purpose,
    )
    log.CreatedResource(pdp_ref.Name(), 'public delegated prefix')
    return result

  def Run(self, args):
    return self._Run(args)


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class CreateBeta(Create):
  r"""Creates a Compute Engine public delegated prefix.

  ## EXAMPLES

  To create a public delegated prefix:

    $ {command} my-public-delegated-prefix --public-advertised-prefix=my-pap \
      --range=120.120.10.128/27 --global
  """

  _api_version = compute_api.COMPUTE_BETA_API_VERSION
  _include_internal_subnetwork_creation_mode = False


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class CreateAlpha(CreateBeta):
  r"""Creates a Compute Engine public delegated prefix.

  ## EXAMPLES

  To create a public delegated prefix:

    $ {command} my-public-delegated-prefix --public-advertised-prefix=my-pap \
      --range=120.120.10.128/27 --global
  """

  _api_version = compute_api.COMPUTE_ALPHA_API_VERSION
  _include_internal_subnetwork_creation_mode = True

  @classmethod
  def Args(cls, parser):
    flags.AddPdpPurpose(parser)
    super(CreateAlpha, cls).Args(parser)

  def Run(self, args):
    return self._Run(args)
