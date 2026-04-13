# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import pytest

from sarif2gha.stdout_writer import StdoutWriter


@pytest.mark.parametrize(
    "src_str",
    [
        (
            '::warning '
            'file=src/foo.py,line=8,col=3,endLine=9,endColumn=80,'
            'title=Warning title'
            '::Main message'
        ),
        (
            "::error "
            "file=samples/Introduction/simple-example.js,line=1,col=5,"
            "title=disallow unused variables"
            "::'x' is assigned a value but never used."
        ),
        (
            "::notice "
            "file=bad-eval.py,line=3,"
            "title=PY2335"
            "::Use of tainted variable 'expr' %0Ain the insecure function 'eval'."
        ),
        (
            ''
        ),
        (
            "::notice "
            "::very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "very very very very very very very very "
            "long string test"
        )
    ]
)


def test_stdout_writer(capsys, src_str):
    """Tests for typical usage of StdoutWriter."""
    writer = StdoutWriter()
    writer.write(src_str)

    captured = capsys.readouterr()
    assert captured.out == src_str + '\n'
