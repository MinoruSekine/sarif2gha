# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from unittest.mock import patch

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
        )
    ]
)


def test_stdout_writer(src_str):
    """Tests for typical usage of StdoutWriter."""
    writer = StdoutWriter()
    with patch('sys.stdout.write') as mock_write:
        writer.write(src_str)

        expected_str = src_str + '\n'
        mock_write.assert_called_once_with(expected_str)
