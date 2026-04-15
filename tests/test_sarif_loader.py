# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from pathlib import Path

import pytest

from sarif2gha.analysis_result import (
    AnalysisResult,
    LoadFailureData,
    LoadSuccessData,
    Severity,
)
from sarif2gha.sarif_loader import SarifLoader

_TESTS_DIR = Path(__file__).parent
_PROJECT_ROOT_DIR = _TESTS_DIR.parent
_SAMPLES_DIR = _PROJECT_ROOT_DIR / "samples"
_SARIF_FILE_EMPTY_LOG = _SAMPLES_DIR / "empty-log.sarif.json"
_SARIF_FILE_RELATED_LOCATIONS = _SAMPLES_DIR / "bad-eval-related-locations.sarif"
_SARIF_FILE_WITH_CODE_FLOW = _SAMPLES_DIR / "bad-eval-with-code-flow.sarif"
_SARIF_FILE_SIMPLE_EXAMPLE = _SAMPLES_DIR / "simple-example.sarif"
_NOT_EXISTING_FILE = _SAMPLES_DIR / "not_existing.sarif"

@pytest.fixture()
def loader() -> SarifLoader:
    """Construct test target loader instance."""
    return SarifLoader()

@pytest.mark.parametrize(
    "sarif_path, expected",
    [
        (
            Path(_SARIF_FILE_SIMPLE_EXAMPLE),
            LoadSuccessData(
                results=[
                    AnalysisResult(
                        file='/C:/dev/sarif/sarif-tutorials/samples/Introduction/simple-example.js',
                        severity=Severity.ERROR,
                        start_line=0,
                        start_column=4,
                        end_line=None,
                        end_column=None,
                        title="disallow unused variables",
                        message="'x' is assigned a value but never used."
                    )
                ]
            )
        ),
        (
            Path(_SARIF_FILE_RELATED_LOCATIONS),
            LoadSuccessData(
                results=[
                    AnalysisResult(
                        file='3-Beyond-basics/bad-eval.py',
                        # If level is absent in SARIF, its value SHALL be "warning".
                        severity=Severity.WARNING,
                        start_line=3,
                        start_column=None,
                        end_line=None,
                        end_column=None,
                        title="PY2335",
                        message=(
                            "Use of tainted variable 'expr'"
                            " in the insecure function 'eval'."
                        )
                    )
                ]
            )
        ),
        (
            Path(_SARIF_FILE_WITH_CODE_FLOW),
            LoadSuccessData(
                results=[
                    AnalysisResult(
                        file='3-Beyond-basics/bad-eval-with-code-flow.py',
                        # If level is absent in SARIF, its value SHALL be "warning".
                        severity=Severity.WARNING,
                        start_line=7,
                        start_column=None,
                        end_line=None,
                        end_column=None,
                        title="PY2335",
                        message=(
                            "Use of tainted variable 'raw_input'"
                            " in the insecure function 'eval'."
                        )
                    )
                ]
            )
        )
    ]
)

def test_sarif_loader(
        loader: SarifLoader,
        sarif_path: Path,
        expected: LoadSuccessData
) -> None:
    """Parameterized tests for typical usages of SarifLoader."""
    loaded_data = loader.load(sarif_path)
    assert isinstance(loaded_data, LoadSuccessData)
    result = loaded_data.results[0]
    expected_result = expected.results[0]
    assert result.file == expected_result.file
    assert result.severity == expected_result.severity
    assert result.start_line == expected_result.start_line
    assert result.start_column == expected_result.start_column
    assert result.end_line == expected_result.end_line
    assert result.end_column == expected_result.end_column
    assert result.title == expected_result.title
    assert result.message == expected_result.message

def test_sarif_loader_empty_log(loader: SarifLoader) -> None:
    """Test for SARIF which includes empty log."""
    loaded_data = loader.load(_SARIF_FILE_EMPTY_LOG)
    assert isinstance(loaded_data, LoadSuccessData)
    results = loaded_data.results
    assert len(results) == 0

def test_sarif_loader_not_existing_file(loader: SarifLoader) -> None:
    """Test for not existing file."""
    assert(isinstance(loader.load(_NOT_EXISTING_FILE), LoadFailureData))
