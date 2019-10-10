#!/usr/bin/env python3

import os
import sys
from shutil import which
from pathlib import Path
from pipx import main, constants

from pipx.util import WINDOWS
from helpers import assert_not_in_virtualenv
from unittest import mock
import pytest

assert_not_in_virtualenv()


@pytest.fixture
def pipx_temp_env(tmp_path, monkeypatch):
    """Sets up temporary paths for pipx to install into.

    Also adds environment variables as necessary to make pip installations
    seamless.
    """
    shared_dir = Path(tmp_path) / "shareddir"
    home_dir = Path(tmp_path) / "subdir" / "pipxhome"
    bin_dir = Path(tmp_path) / "otherdir" / "pipxbindir"

    monkeypatch.setattr(constants, "PIPX_SHARED_LIBS", shared_dir)
    monkeypatch.setattr(constants, "PIPX_HOME", home_dir)
    monkeypatch.setattr(constants, "LOCAL_BIN_DIR", bin_dir)
    monkeypatch.setattr(constants, "PIPX_LOCAL_VENVS", home_dir / "venvs")

    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)


def test_install(capsys, pipx_temp_env, caplog):
    with mock.patch.object(sys, "argv", ["pipx", "install", "pycowsay", "--verbose"]):
        main.cli()
    captured = capsys.readouterr()
    assert "installed package pycowsay" in captured.out
    assert "symlink missing or pointing to unexpected location" not in captured.out
    assert "not modifying" not in captured.out
    assert "is not on your PATH environment variable" not in captured.out

    for record in caplog.records:
        assert "⚠️" not in record.message
        assert "WARNING" not in record.message


def test_help_text(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["pipx", "install", "--help"])

    mock_exit = mock.Mock(side_effect=ValueError("raised in test to exit early"))
    with mock.patch.object(sys, "exit", mock_exit), pytest.raises(
        ValueError, match="raised in test to exit early"
    ):
        main.cli()
    captured = capsys.readouterr()
    assert "apps you can run from anywhere" in captured.out


#     def test_install(self):
#         easy_packages = ["pycowsay", "black"]
#         tricky_packages = ["cloudtoken", "awscli", "ansible", "shell-functools"]
#         if WINDOWS:
#             all_packages = easy_packages
#         else:
#             all_packages = easy_packages + tricky_packages

#         for package in all_packages:
#             subprocess.run([self.pipx_bin, "install", package], check=True)

#         ret = subprocess.run(
#             [self.pipx_bin, "list"], check=True, stdout=subprocess.PIPE
#         )

#         for package in all_packages:
#             self.assertTrue(package in ret.stdout.decode())

#     def setUp(self):
#         """install pipx to temporary directory and save pipx binary path"""

#         temp_dir = tempfile.TemporaryDirectory(prefix="pipx_tests_")
#         home_dir = Path(temp_dir.name) / "subdir" / "pipxhome"
#         bin_dir = Path(temp_dir.name) / "otherdir" / "pipxbindir"

#         Path(temp_dir.name).mkdir(exist_ok=True)
#         env = os.environ
#         env["PIPX_SHARED_LIBS"] = str(self._shared_dir.name)
#         env["PIPX_HOME"] = str(home_dir)
#         env["PIPX_BIN_DIR"] = str(bin_dir)

#         if WINDOWS:
#             pipx_bin = "pipx.exe"
#         else:
#             pipx_bin = "pipx"

#         self.assertTrue(which(pipx_bin))
#         self.pipx_bin = pipx_bin
#         self.temp_dir = temp_dir
#         self.bin_dir = bin_dir
#         print()  # blank line to unit tests doesn't get overwritten by pipx output

#     def tearDown(self):
#         self.temp_dir.cleanup()

