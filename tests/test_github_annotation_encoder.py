# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import pytest

from sarif2gha.analysis_result import AnalysisResult, Severity
from sarif2gha.github_annotation_encoder import GitHubAnnotationEncoder


@pytest.fixture()
def encoder():
    """Construct test target encoder instance."""
    return GitHubAnnotationEncoder()

@pytest.mark.parametrize(
    "analysis_result, expected_str",
    [
        pytest.param(
            AnalysisResult(
                file='src/foo.py',
                severity=Severity.WARNING,
                start_line=7,
                start_column=2,
                end_line=8,
                end_column=79,
                title='Warning title',
                message='Main message'
            ),
            '::warning '
            'file=src/foo.py,line=8,col=3,endLine=9,endColumn=80,'
            'title=Warning title'
            '::Main message',
            id='warning_full_param'
        ),
        pytest.param(
            AnalysisResult(
                file='Introduction/simple-example.js',
                severity=Severity.ERROR,
                start_line=0,
                start_column=4,
                end_line=None,
                end_column=None,
                title='disallow unused variables',
                message="'x' is assigned a value but never used."
            ),
            "::error "
            "file=Introduction/simple-example.js,line=1,col=5,"
            "title=disallow unused variables"
            "::'x' is assigned a value but never used.",
            id='error_without_any_ends'
        ),
        pytest.param(
            AnalysisResult(
                file='Beyond-basics/bad-eval.py',
                severity=Severity.NOTICE,
                start_line=2,
                start_column=None,
                end_line=None,
                end_column=None,
                title='PY2335',
                message=(
                    "Use of tainted variable 'expr' \n"
                    "in the insecure function 'eval'."
                )
            ),
            "::notice "
            "file=Beyond-basics/bad-eval.py,line=3,"
            "title=PY2335"
            "::Use of tainted variable 'expr' %0Ain the insecure function 'eval'.",
            id='notice_with_escape'
        )
    ]
)

def test_github_annotation_encoder(encoder, analysis_result, expected_str):
    """Parameterized tests for typical usages of GitHubAnnotationEncoder."""
    encoded_str = encoder.encode(analysis_result)
    assert encoded_str == expected_str
