# -*- coding: utf-8 -*- #
# Copyright 2023 Google LLC. All Rights Reserved.
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
"""Command that statically validates gcloud commands for corectness.

To validate a command, run:

```
gcloud meta lint-gcloud-commands --command-string="gcloud compute instances
list"
```

To validate a list of commands in a file:

1) Create a JSON file with the following format:

```
[
  {
    "command_string": "gcloud compute instances list",
  },
  {
    "command_string": "gcloud compute instances describe my-instance",
  }
]
```

2) Then run the command:

```
gcloud meta lint-gcloud-commands --commands-file=commands.json
```

Commands can also be associated with an ID, which will be used to identify the
command in the output. Simply run:

```
gcloud meta lint-gcloud-commands --commands-file=commands.json --serialize
```
This will associated each command with using the index it was found in the file
as the ID. If you want to associate a command with a specific ID, you can do so
by adding the `id` field to the command in the JSON file. For example:

```
[
  {
    "command_string": "gcloud compute instances list",
    "id": 0,
  },
  {
    "command_string": "gcloud compute instances describe my-instance",
    "id": 1,
  }
]
```

This will output the validation results in the following format:

```
{"0": [{<OUTPUT_1>}], "1": [{<OUTPUT_2>}]}
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import copy
import json
import os
import re
import shlex
from typing import collections

from googlecloudsdk import gcloud_main
from googlecloudsdk.calliope import base
from googlecloudsdk.calliope import exceptions as gcloud_exceptions
from googlecloudsdk.command_lib.meta import generate_argument_spec
from googlecloudsdk.core import log
from googlecloudsdk.core import yaml
from googlecloudsdk.core.util import files
import six


_PARSING_OUTPUT_TEMPLATE = {
    'command_string': None,
    'success': False,
    'command_args': None,
    'command_string_no_args': None,
    'args_structure': {},
    'error_message': None,
    'error_type': None,
}

_IGNORE_ARGS = ['--help']


class CommandValidationError(Exception):
  pass


def _read_commands_from_file(commands_file):
  """Reads commands from a JSON file."""
  with files.FileReader(commands_file) as f:
    command_file_data = json.load(f)
  ref_id = 0
  command_strings = {}
  needs_id = any(command_data.get('id') for command_data in command_file_data)
  for command_data in command_file_data:
    command_id = command_data.get('id')
    if needs_id and command_id is None:
      raise ValueError(
          'Not all commands have an ID. Id for command'
          f' {command_data["command_string"]} is None.'
      )
    command_strings[command_data['command_string']] = command_id or ref_id
    ref_id += 1
  return command_strings


def _separate_command_arguments(command_string: str):
  """Move all flag arguments to back."""
  command_string = command_string.split('#')[0]
  try:
    # Split arguments
    if os.name == 'nt':
      command_arguments = shlex.split(command_string, posix=False)
    else:
      command_arguments = shlex.split(command_string)
  except Exception:  # pylint: disable=broad-except
    raise CommandValidationError(
        'Command could not be validated due to unforeseen edge case.'
    )
  # Move any flag arguments to end of command.
  flag_args = [arg for arg in command_arguments if arg.startswith('--')]
  command_args = [arg for arg in command_arguments if not arg.startswith('--')]
  return command_args + flag_args


def _add_equals_to_flags(command):
  """Adds equals signs to gcloud command flags, except for format and help flags."""

  pattern = (  # Matches flag name and its value (excluding format and help)
      r'(--[a-zA-Z0-9-]+) +([^-][^ ]*)'
  )
  replacement = r'\1=\2'  # Inserts equals sign between flag and
  modified_command = re.sub(pattern, replacement, command)
  # Remove = from flags without explicit values
  modified_command = re.sub(r'(--[a-zA-Z0-9-]+)= ', r'\1 ', modified_command)
  return modified_command


def formalize_gcloud_command(command_str):
  command_str = _add_equals_to_flags(command_str)
  command_str = (
      command_str.replace('--project=PROJECT ', '--project=my-project ')
      .replace('--project=PROJECT_ID ', '--project=my-project ')
      .replace('$PROJECT_ID ', 'my-project ')
      .replace('YOUR_PROJECT_ID ', 'my-project ')
  )
  return command_str


def _extract_gcloud_commands(text):
  """Extracts code snippets from fenced code blocks within a text string.

  Args:
      text: The text string containing fenced code blocks.

  Returns:
      A list of extracted code snippets.
  """
  text = bytes(text, 'utf-8').decode('unicode_escape')
  fenced_pattern = r'```(?:[\w ]+\n)?(.*?)```'
  indented_pattern = (  # 3-8 indented spaces as arbitray nums
      r'(?: {3-8}|\t)(.*?)(?:\n\S|\n$)'
  )
  combined_pattern = re.compile(
      f'{fenced_pattern}|{indented_pattern}', re.DOTALL
  )

  code_snippets = []
  for match in combined_pattern.finditer(
      text
  ):  # use finditer instead of findall
    command_str = match.group(1).strip()
    if 'gcloud ' not in command_str or not command_str.startswith('gcloud'):
      continue
    for cmd in command_str.split('gcloud '):
      cmd_new_lines = cmd.split('\n')
      if len(cmd_new_lines) >= 1 and cmd_new_lines[0].strip():
        command_str = formalize_gcloud_command(cmd_new_lines[0].strip())
        code_snippets.append(f'gcloud {command_str}')
  return code_snippets


def _get_command_node(command_arguments):
  """Returns the command node for the given command arguments."""
  cli = gcloud_main.CreateCLI([])
  command_arguments = command_arguments[1:]
  current_command_node = cli._TopElement()  # pylint: disable=protected-access
  for argument in command_arguments:
    if argument.startswith('--'):
      break
    child_command_node = current_command_node.LoadSubElement(argument)
    if not child_command_node:
      break
    current_command_node = child_command_node
  return current_command_node


def _get_command_no_args(command_node):
  """Returns the command string without any arguments."""
  return ' '.join(command_node.ai.command_name)


def _get_command_args_tree(command_node):
  """Returns the command string without any arguments."""
  argument_tree = generate_argument_spec.GenerateArgumentSpecifications(
      command_node
  )
  return argument_tree


def _get_positional_metavars(args_tree):
  """Returns a dict of positional metavars."""

  positional_args = []

  def _process_arg(node):
    if 'name' in node and node.get('positional', False):
      if node['name']:
        positional_args.append(node['name'])

  def _traverse_arg_group(node):
    for arg in node:
      _traverse_tree(arg)

  def _traverse_tree(node):
    if 'group' in node:
      group = node['group']['arguments']
      _traverse_arg_group(group)
    else:
      _process_arg(node)

  for node in args_tree:
    _traverse_tree(node)
  return positional_args


def _normalize_command_args(command_args, args_tree):
  """Normalizes command args for storage."""

  positionals_used = set()
  arg_name_value = {}
  positional_args_in_tree = _get_positional_metavars(args_tree['arguments'])

  def _sort_command_args(args):
    """Sorts command arguments.

    Arguments starting with '--' are placed at the back, and all arguments are
    ordered alphabetically.

    Args:
      args: The command arguments to sort.

    Returns:
      The sorted command arguments.
    """
    flag_args = sorted([arg for arg in args if arg.startswith('--')])
    positional_args = [arg for arg in args if not arg.startswith('--')]
    return positional_args + flag_args

  command_args = _sort_command_args(command_args)

  def _get_next_available_positional_arg():
    for positional_metavar in positional_args_in_tree:
      if positional_metavar not in positionals_used:
        command_value = command_arg
        command_arg_name = positional_metavar.upper()
        positionals_used.add(positional_metavar)
        return command_arg_name, command_value
    return None, None

  arg_index = 0
  for command_arg in command_args:
    command_arg_name = command_arg
    if command_arg.startswith('--'):
      equals_index = command_arg.find('=')
      if equals_index != -1:
        command_arg_name = command_arg[:equals_index]
        command_value = command_arg[equals_index + 1 :]
      else:
        command_value = ''
    else:
      # Positional argument
      command_arg_name, command_value = _get_next_available_positional_arg()
      # Arg should be included in output, regardless of whether it a real
      # positional arg or not.
      command_arg_name = command_arg_name or command_arg
      command_value = command_value or ''
    arg_name_value[command_arg_name] = {
        'value': command_value,
        'index': arg_index,
    }
    arg_index += 1
  return collections.OrderedDict(
      sorted(arg_name_value.items(), key=lambda item: item[1]['index'])
  )


@base.UniverseCompatible
class GenerateCommand(base.Command):
  """Generate YAML file to implement given command.

  The command YAML file is generated in the --output-dir directory.
  """

  _INDEXED_VALIDATION_RESULTS = collections.OrderedDict()
  _SERIALIZED_VALIDATION_RESULTS = collections.OrderedDict()
  _VALIDATION_RESULTS = []
  index_results = False
  serialize_results = False

  def _validate_command(self, command_string, ref_id=0):
    """Validate a single command."""
    command_string = formalize_gcloud_command(command_string)
    command_arguments = _separate_command_arguments(command_string)
    command_success, command_node, flag_arguments = (
        self._validate_command_prefix(command_arguments, command_string, ref_id)
    )
    if not command_success:
      return
    flag_success = self._validate_command_suffix(
        command_node, flag_arguments, command_string, ref_id
    )
    if not flag_success:
      return
    self._store_validation_results(True, command_string, ref_id, flag_arguments)

  def _validate_commands_from_file(self, commands_file):
    """Validate multiple commands given in a file."""
    commands = _read_commands_from_file(commands_file)
    for command, ref_id in commands.items():
      try:
        self._validate_command(command, ref_id)
      except Exception as e:  # pylint: disable=broad-except
        self._store_validation_results(
            False,
            command,
            ref_id,
            None,
            f'Command could not be validated: {e}',
            'CommandValidationError',
        )

  def _validate_commands_from_text(self, commands_text_file):
    """Validate multiple commands given in a text string."""
    with files.FileReader(commands_text_file) as f:
      text = f.read()
    commands = _extract_gcloud_commands(text)
    ref_id = 0
    for command in commands:
      self._validate_command(command, ref_id)
      ref_id += 1

  def _validate_command_prefix(self, command_arguments, command_string, ref_id):
    """Validate that the argument string contains a valid command or group."""
    cli = gcloud_main.CreateCLI([])
    # Remove "gcloud" from command arguments.
    command_arguments = command_arguments[1:]
    index = 0
    current_command_node = cli._TopElement()  # pylint: disable=protected-access
    for argument in command_arguments:
      # If this hits, we've found a command group with a flag passed.
      # e.g. gcloud compute --help
      if argument.startswith('--'):
        return (
            True,
            current_command_node,
            command_arguments[index:],
        )
      # Attempt to load next section of command path.
      current_command_node = current_command_node.LoadSubElement(argument)
      # If not a valid section of command path, fail validation.
      if not current_command_node:
        self._store_validation_results(
            False,
            command_string,
            ref_id,
            command_arguments[index:],
            "Invalid choice: '{}'".format(argument),
            'UnrecognizedCommandError',
        )
        return False, None, None
      index += 1
      # If command path is valid and is a command, return the command node.
      if not current_command_node.is_group:
        return (
            True,
            current_command_node,
            command_arguments[index:],
        )

    # If we make it here then only a command group has been provided.
    remaining_flags = command_arguments[index:]
    if not remaining_flags:
      self._store_validation_results(
          False,
          command_string,
          ref_id,
          command_arguments[index:],
          'Command name argument expected',
          'UnrecognizedCommandError',
      )
      return False, None, None
    # If we've iterated through the entire list and end up here, something
    # unpredicted has happened.
    raise CommandValidationError(
        'Command could not be validated due to unforeseen edge case.'
    )

  def _validate_command_suffix(
      self, command_node, command_arguments, command_string, ref_id
  ):
    """Validates that the given flags can be parsed by the argparse parser."""
    for ignored_arg in _IGNORE_ARGS:
      if ignored_arg in command_arguments:
        return True
    found_parent = False
    if command_arguments:
      for command_arg in command_arguments:
        if (
            '--project' in command_arg
            or '--folder' in command_arg
            or '--organization' in command_arg
        ):
          found_parent = True
    if not command_arguments:
      command_arguments = []
    if not found_parent:
      command_arguments.append('--project=myproject')
    try:
      command_node._parser.parse_args(command_arguments, raise_error=True)  # pylint: disable=protected-access
    except (
        files.MissingFileError,
        gcloud_exceptions.BadFileException,
        yaml.FileLoadError,
    ):
      pass
    except argparse.ArgumentError as e:
      if 'No such file or directory' in str(e):
        return True
      self._store_validation_results(
          False,
          command_string,
          ref_id,
          command_arguments,
          six.text_type(e),
          type(e).__name__,
      )
      return False
    return True

  def _store_validation_results(
      self,
      success,
      command_string,
      ref_id,
      command_args=None,
      error_message=None,
      error_type=None,
  ):
    """Store information related to the command validation."""
    validation_output = copy.deepcopy(_PARSING_OUTPUT_TEMPLATE)
    validation_output['command_string'] = command_string
    try:
      command_node = _get_command_node(
          _separate_command_arguments(command_string)
      )
      validation_output['command_string_no_args'] = _get_command_no_args(
          command_node
      )
      validation_output['args_structure'] = _get_command_args_tree(command_node)
    except Exception:  # pylint: disable=broad-except
      validation_output['command_string_no_args'] = command_string
    if command_args:
      validation_output['command_args'] = _normalize_command_args(
          command_args, validation_output['args_structure']
      )
    validation_output['success'] = success
    validation_output['error_message'] = error_message
    validation_output['error_type'] = error_type
    sorted_validation_output = collections.OrderedDict(
        sorted(validation_output.items())
    )
    if self.serialize_results:
      if ref_id not in self._SERIALIZED_VALIDATION_RESULTS:
        self._SERIALIZED_VALIDATION_RESULTS[ref_id] = [sorted_validation_output]
      else:
        self._SERIALIZED_VALIDATION_RESULTS[ref_id].append(
            sorted_validation_output
        )
    if self.index_results:
      self._INDEXED_VALIDATION_RESULTS[command_string] = (
          sorted_validation_output
      )
    else:
      self._VALIDATION_RESULTS.append(sorted_validation_output)

  def _log_validation_results(self):
    """Output collected validation results."""
    if self.index_results:
      log.out.Print(json.dumps(self._INDEXED_VALIDATION_RESULTS))
    elif self.serialize_results:
      log.out.Print(json.dumps(self._SERIALIZED_VALIDATION_RESULTS))
    else:
      log.out.Print(json.dumps(self._VALIDATION_RESULTS))

  @staticmethod
  def Args(parser):
    command_group = parser.add_group(mutex=True)
    command_group.add_argument(
        '--command-string',
        help='Gcloud command to statically validate.',
    )
    command_group.add_argument(
        '--commands-file',
        help='JSON file containing list of gcloud commands to validate.',
    )
    command_group.add_argument(
        '--commands-text-file',
        help=(
            'Raw text containing gcloud command(s) to validate. For example,'
            ' the commands could be in fenced code blocks or indented code'
            ' blocks.'
        ),
    )
    parser.add_argument(
        '--serialize',
        action='store_true',
        help='Output results in a dictionary serialized by reference id.',
    )

  def Run(self, args):
    if args.serialize:
      self.serialize_results = True
    if args.IsSpecified('command_string'):
      self._validate_command(args.command_string)
    elif args.IsSpecified('commands_text_file'):
      self._validate_commands_from_text(args.commands_text_file)
    else:
      self._validate_commands_from_file(args.commands_file)
    self._log_validation_results()
