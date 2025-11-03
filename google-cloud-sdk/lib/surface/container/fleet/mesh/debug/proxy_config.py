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
"""A group of commands used to retrieve information about proxy configuration from the Envoy config dump."""

from googlecloudsdk.api_lib.container.fleet import debug_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.container.fleet import resources
from googlecloudsdk.command_lib.container.fleet.mesh import istioctl_backend
from googlecloudsdk.core import properties

EXAMPLES = r"""
    To retrieve the type cluster config dump for Pod instance pn.default.

    ${command} pn.default
              --type=cluster
              --project=projectId
              --membership=membershipId
              --location=us-central1
              --ouput=yaml
"""


@base.DefaultUniverseOnly
class ProxyConfig(base.BinaryBackedCommand):
  """Retrieve a configuration summary for a given Envoy instance.
  """
  detailed_help = {'EXAMPLES': EXAMPLES}

  @staticmethod
  def Args(parser):
    resources.AddMembershipResourceArg(
        parser,
        plural=False,
        membership_required=True,
        membership_help='Name of the membership to troubleshoot against.',
    )

    parser.add_argument(
        'pod_name_namespace',
        help='Pod to check against. Use in format of <pod-name[.Namespace]>',
    )

    proxy_config_type = base.ChoiceArgument(
        '--type',
        required=True,
        choices=[
            'bootstrap',
            'cluster',
            'clusters',
            'endpoint',
            'endpoints',
            'listener',
            'listeners',
            'log',
            'route',
            'routes',
            'secret',
            'secrets',
        ],
        help_str=(
            'Proxy configuration type to retrieve. \n\n '
            ' bootstrap            Retrieves bootstrap configuration for the'
            ' Envoy in the specified pod \n clusters/cluster     Retrieves'
            ' cluster configuration for the Envoy in the specified pod \n'
            ' endpoints/endpoint   Retrieves endpoint configuration for the'
            ' Envoy in the specified pod \n listeners/listener   Retrieves'
            ' listener configuration for the Envoy in the specified pod \n log '
            '                 Retrieves logging levels of the Envoy in the'
            ' specified pod \n routes/route         Retrieves route'
            ' configuration for the Envoy in the specified pod \n'
            ' secrets/secret       Retrieves secret configuration for the Envoy'
            ' in the specified pod \n'
        ),
    )
    proxy_config_type.AddToParser(parser)
    parser.add_argument(
        '--output',
        choices=['json', 'yaml'],
        required=False,
        help=(
            'Return the detailed proxy config. The output format is either json'
            ' or yaml.'
        ),
    )

    parser.add_argument(
        '--fqdn',
        required=False,
        help=(
            'Filter clusters by substring of Service FQDN field. If'
            ' unspecified, all clusters will be included in the output"'
        ),
    )

  def Run(self, args):
    command_executor = istioctl_backend.IstioctlWrapper()
    # Generate kubecontext
    context = debug_util.ContextGenerator(args)

    auth_cred = istioctl_backend.GetAuthToken(
        account=properties.VALUES.core.account.Get(), operation='apply'
    )
    response = command_executor(
        command='proxy-config',
        context=context,
        env=istioctl_backend.GetEnvArgsForCommand(
            extra_vars={'GCLOUD_AUTH_PLUGIN': 'true'}
        ),
        proxy_config_type=args.type,
        pod_name_namespace=args.pod_name_namespace,
        output_format=args.output,
        fqdn=args.fqdn,
        stdin=auth_cred,
    )
    return response
