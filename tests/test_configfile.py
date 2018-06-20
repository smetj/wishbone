#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_configfile.py
#
#  Copyright 2017 Jelle Smet <development@smetj.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from wishbone.config.configfile import ConfigFile
from os import remove
from easydict import EasyDict

HELLO_WORLD = """
modules:
  input:
    module: wishbone.module.input.generator
    arguments:
      payload: hello world

  output:
    module: wishbone.module.output.stdout

routingtable:
  - input.outbox -> output.inbox
"""


def setup_module(module):

    try:
        remove("/tmp/.test_bootstrap.yaml")
    except Exception:
        pass

    with open("/tmp/.test_bootstrap.yaml", "w") as f:
        f.write(HELLO_WORLD)
        f.close()


def teardown_module(module):

    remove("/tmp/.test_bootstrap.yaml")


class Test_ConfigFile:
    def test_dump_type(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "SYSLOG")
        assert isinstance(c.dump(), EasyDict)

    def test_default_template_functions(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "SYSLOG")
        assert sorted(c.dump()["template_functions"]) == sorted(
            ["strftime", "epoch", "version", "env"]
        )

    def test_syslog_setup(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "SYSLOG")
        assert "_logs_syslog" in c.dump()["modules"]
        assert (
            c.dump()["modules"]["_logs_syslog"]["module"]
            == "wishbone.module.output.syslog"
        )
        assert c.dump()["modules"]["_logs"]["module"] == "wishbone.module.flow.funnel"

    def test_stdout_setup(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "STDOUT")
        assert "_logs_stdout" in c.dump()["modules"]
        assert (
            c.dump()["modules"]["_logs_stdout"]["module"]
            == "wishbone.module.output.stdout"
        )

    def test_logfilter_setup(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "STDOUT")
        assert "_logs_filter" in c.dump()["modules"]
        assert (
            c.dump()["modules"]["_logs_filter"]["module"]
            == "wishbone.module.flow.queueselect"
        )

    def test_metrics_setup(self):

        c = ConfigFile("/tmp/.test_bootstrap.yaml", "STDOUT")
        assert "_metrics" in c.dump()["modules"]
        assert (
            c.dump()["modules"]["_metrics"]["module"] == "wishbone.module.flow.funnel"
        )
