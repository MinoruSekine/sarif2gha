# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from dataclasses import dataclass
from enum import Enum, auto


class Severity(Enum):
    """Enum to indicate sevrity of each item."""
    ERROR = auto()
    WARNING = auto()
    NOTICE = auto()
    UNKNOWN = auto()

@dataclass
class AnalysisResult:
    """Structure for each item reported by external tools."""
    file: str = ""
    severity: Severity = Severity.UNKNOWN
    title: str | None = None
    message: str = ""
    start_line: int | None = None
    start_column: int | None = None
    end_line: int | None = None
    end_column: int | None = None

@dataclass
class LoadSuccessData:
    """Data structure for successful load."""
    results: list[AnalysisResult]

@dataclass
class LoadFailureData:
    """Data structure for load failure."""
    message: str = ""
