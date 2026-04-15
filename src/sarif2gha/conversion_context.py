# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from pathlib import Path
from typing import Protocol

from sarif2gha.analysis_result import (
    AnalysisResult,
    LoadFailureData,
    LoadSuccessData,
)


class Loader(Protocol):
    def load(self, sarif_path: Path) -> LoadSuccessData | LoadFailureData: ...

class Encoder(Protocol):
    def encode(self, analysis_result: AnalysisResult) -> str: ...

class Writer(Protocol):
    def write(self, src_str: str) -> None: ...

class ConversionContext:
    """Context to convert analysis input to output."""
    _sarif_path: Path

    def __init__(
            self,
            sarif_path: Path,
            loader: Loader,
            encoder: Encoder,
            writer: Writer
    ) -> None:
        """Contructor."""
        self._sarif_path = sarif_path
        self._loader = loader
        self._encoder = encoder
        self._writer = writer

    def run(self) -> str | None:
        """Run conversion."""
        load_data = self._loader.load(self._sarif_path)
        if isinstance(load_data, LoadSuccessData):
            for i in load_data.results:
                self._writer.write(self._encoder.encode(i))
            return None
        if isinstance(load_data, LoadFailureData):
            return load_data.message
        raise ValueError("Unknown return value from loader.")
