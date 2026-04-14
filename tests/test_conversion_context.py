# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from sarif2gha.analysis_result import (
    AnalysisResult,
    LoadFailureData,
    LoadSuccessData,
    Severity,
)
from sarif2gha.conversion_context import ConversionContext


@pytest.mark.parametrize(
    "src_sarif_file_path, analysis_results, encoded_strs",
    [
        pytest.param(
            Path("samples/simple-example.sarif"),
            LoadSuccessData(
                results=[
                    AnalysisResult(
                        file='/C:/dev/sarif/sarif-tutorials/samples/Introduction/simple-example.js',
                        severity=Severity.ERROR,
                        start_line=0,
                        start_column=4,
                        end_line=None,
                        end_column=None,
                        title='disallow unused variables',
                        message="'x' is assigned a value but never used."
                    )
                ]
            ),
            [
                (
                    "::error "
                    "file=samples/Introduction/simple-example.js,line=1,col=5,"
                    "title=disallow unused variables"
                    "::'x' is assigned a value but never used."
                )
            ],
            id='simple-example.sarif'
        ),
        pytest.param(
            Path("samples/empty-log.sarif.json"),
            LoadSuccessData(
                results=[]
            ),
            [],
            id='samples/empty-log.sarif.json'
        ),
        pytest.param(
            Path("samples/bad-eval-related-locations.sarif"),
            LoadSuccessData(
                results=[
                    AnalysisResult(
                        file='3-Beyond-basics/bad-eval.py',
                        severity=Severity.WARNING,
                        start_line=3,
                        start_column=None,
                        end_line=None,
                        end_column=None,
                        title='disallow unused variables',
                        message=(
                            "Use of tainted variable 'expr' "
                            "in the insecure function 'eval'."
                        )
                    )
                ]
            ),
            [
                (
                    "::warning "
                    "file=3-Beyond-basics/bad-eval.py,line=4,"
                    "title=PY2335"
                    "::'x' is assigned a value but never used."
                )
            ],
            id='bad-eval-related-locations.sarif'
        ),
        pytest.param(
            Path("samples/several-results.sarif"),
            LoadSuccessData(
                results=[
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
                    AnalysisResult(
                        file='3-Beyond-basics/bad-eval.py',
                        severity=Severity.WARNING,
                        start_line=3,
                        start_column=None,
                        end_line=None,
                        end_column=None,
                        title='disallow unused variables',
                        message=(
                            "Use of tainted variable 'expr' "
                            "in the insecure function 'eval'."
                        )
                    )
                ]
            ),
            [
                (
                    "::error "
                    "file=Introduction/simple-example.js,line=1,col=5,"
                    "title=disallow unused variables"
                    "::'x' is assigned a value but never used."
                ),
                (
                    "::warning "
                    "file=3-Beyond-basics/bad-eval.py,line=4,"
                    "title=PY2335"
                    "::'x' is assigned a value but never used."
                )
            ],
            id='several-results'
        ),
        pytest.param(
            "samples/load_failure_data.sarif",
            LoadFailureData(
                message="Load failed."
            ),
            [],
            id='load_failure_data.sarif'
        )
    ]
)


def test_conversion_context(
        src_sarif_file_path,
        analysis_results,
        encoded_strs
):
    """Tests for ConversionContext."""
    # Setup mocks.
    mock_loader = MagicMock()
    mock_loader.load.return_value = analysis_results

    mock_encoder = MagicMock()
    mock_encoder.encode.side_effect = encoded_strs

    mock_writer = MagicMock()

    # Invoke the test target.
    context = ConversionContext(
        src_sarif_file_path,
        mock_loader,
        mock_encoder,
        mock_writer
    )
    run_result = context.run()

    # Validate mock methods calls.
    mock_loader.load.assert_called_once_with(src_sarif_file_path)

    if isinstance(analysis_results, LoadSuccessData):
        assert run_result is None
        if len(analysis_results.results) > 0:
            mock_encoder.encode.assert_has_calls(
                [call(i) for i in analysis_results.results]
            )
            assert mock_encoder.encode.call_count == len(analysis_results.results)
        else:
            mock_encoder.encode.assert_not_called()

        if len(encoded_strs) > 0:
            mock_writer.write.assert_has_calls([call(i) for i in encoded_strs])
            assert mock_writer.write.call_count == len(encoded_strs)
        else:
            mock_writer.write.assert_not_called()
    else:
        assert isinstance(analysis_results, LoadFailureData)
        assert run_result == analysis_results.message
        mock_encoder.encode.assert_not_called()
        mock_writer.write.assert_not_called()

