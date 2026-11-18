#!/usr/bin/env python
#
# Copyright 2012 Google Inc. All Rights Reserved.
"""Python script for interacting with BigQuery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import pdb
import sys
import traceback

# Add to path dependencies if present.
_THIRD_PARTY_DIR = os.path.join(os.path.dirname(__file__), 'third_party')
if os.path.isdir(_THIRD_PARTY_DIR) and _THIRD_PARTY_DIR not in sys.path:
  sys.path.insert(0, _THIRD_PARTY_DIR)

# This strange import below ensures that the correct 'google' is imported.
# We reload after sys.path is updated, so we know if we'll find our google
# before any other.
# pylint:disable=g-import-not-at-top
if 'google' in sys.modules:
  import google

  try:
    reload(google)
  except NameError:
    import importlib

    importlib.reload(google)

from absl import flags

from pyglib import appcommands

# pylint: disable=g-bad-import-order

import bq_flags
import bq_utils
import credential_loader

from frontend import bigquery_command
from frontend import bq_cached_client
from frontend import commands_iam
from frontend import command_cancel
from frontend import command_copy
from frontend import command_delete
from frontend import command_extract
from frontend import command_head
from frontend import command_info
from frontend import command_init
from frontend import command_insert
from frontend import command_list
from frontend import command_load
from frontend import command_make
from frontend import command_mkdef
from frontend import command_partition
from frontend import command_query
from frontend import command_repl
from frontend import command_show
from frontend import command_truncate
from frontend import command_undelete
from frontend import command_update
from frontend import command_version
from frontend import command_wait
from frontend import utils as frontend_utils

flags.adopt_module_key_flags(bq_flags)

FLAGS = flags.FLAGS



# pylint: enable=g-bad-name


def main(unused_argv):
  # Avoid using global flags in main(). In this command line:
  # bq <global flags> <command> <global and local flags> <command args>,
  # only "<global flags>" will parse before main, not "<global and local flags>"


  try:
    frontend_utils.ValidateGlobalFlags()

    bq_commands = {
        # Keep the commands alphabetical.
        'add-iam-policy-binding': commands_iam.AddIamPolicyBinding,
        'cancel': command_cancel.Cancel,
        'cp': command_copy.Copy,
        'extract': command_extract.Extract,
        'get-iam-policy': commands_iam.GetIamPolicy,
        'head': command_head.Head,
        'info': command_info.Info,
        'init': command_init.Init,
        'insert': command_insert.Insert,
        'load': command_load.Load,
        'ls': command_list.ListCmd,
        'mk': command_make.Make,
        'mkdef': command_mkdef.MakeExternalTableDefinition,
        'partition': command_partition.Partition,
        'query': command_query.Query,
        'remove-iam-policy-binding': commands_iam.RemoveIamPolicyBinding,
        'rm': command_delete.Delete,
        'set-iam-policy': commands_iam.SetIamPolicy,
        'shell': command_repl.Repl,
        'show': command_show.Show,
        'truncate': command_truncate.Truncate,
        'undelete': command_undelete.Undelete,
        'update': command_update.Update,
        'version': command_version.Version,
        'wait': command_wait.Wait,
    }

    for command, function in bq_commands.items():
      if command not in appcommands.GetCommandList():
        appcommands.AddCmd(command, function)

  except KeyboardInterrupt as e:
    print('Control-C pressed, exiting.')
    sys.exit(1)
  except BaseException as e:  # pylint: disable=broad-except
    print('Error initializing bq client: %s' % (e,))
    # Use global flags if they're available, but we're exitting so we can't
    # count on global flag parsing anyways.
    if FLAGS.debug_mode or FLAGS.headless:
      traceback.print_exc()
      if not FLAGS.headless:
        pdb.post_mortem()
    sys.exit(1)


# pylint: disable=g-bad-name
def run_main():
  """Function to be used as setuptools script entry point.

  Appcommands assumes that it always runs as __main__, but launching
  via a setuptools-generated entry_point breaks this rule. We do some
  trickery here to make sure that appcommands and flags find their
  state where they expect to by faking ourselves as __main__.
  """

  # Put the flags for this module somewhere the flags module will look
  # for them.
  new_name = sys.argv[0]
  sys.modules[new_name] = sys.modules['__main__']
  for flag in FLAGS.flags_by_module_dict().get(__name__, []):
    FLAGS.register_flag_by_module(new_name, flag)
    for key_flag in FLAGS.key_flags_by_module_dict().get(__name__, []):
      FLAGS.register_key_flag_for_module(new_name, key_flag)

  # Now set __main__ appropriately so that appcommands will be
  # happy.
  sys.modules['__main__'] = sys.modules[__name__]
  appcommands.Run()
  sys.modules['__main__'] = sys.modules.pop(new_name)


if __name__ == '__main__':
  appcommands.Run()
