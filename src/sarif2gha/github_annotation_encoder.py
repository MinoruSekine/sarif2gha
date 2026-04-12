# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import re
from pathlib import PureWindowsPath

from sarif2gha.analysis_result import AnalysisResult, Severity


class GitHubAnnotationEncoder:
    _normalized_project_root_dir: str

    def __init__(self, project_root_dir_path: str):
        """
        Constructor.

        Args:
            project_root_dir_path: Project root dir to resolve paths in SARIF.
        """
        self._normalized_project_root_dir = self._normalize_dir(project_root_dir_path)

    """Encoder for GitHub Annotation style string from analysis data."""
    def encode(self, analysis_result: AnalysisResult) -> str:
        """Encode GitHub Annotation string from AnalysisResult instance."""
        if '\\' in analysis_result.file:
            raise ValueError(
                f"analysis_result.file must use forward slashes, "
                f"got: {analysis_result.file!r}"
            )
        encoded_str = f"::{self._encode_severity(analysis_result.severity)} "
        file = self._resolve_as_project_root_relative_path(analysis_result.file)
        encoded_str += f"file={self._encode_property_str(file)}"
        if analysis_result.start_line is not None:
            if analysis_result.start_line < 0:
                raise ValueError(
                    f"start_line must be >= 0 (actual:{analysis_result.start_line})")
            encoded_str += f",line={analysis_result.start_line + 1}"
            # `col`, `endLine`, and `endColumn` have no meaning without `line`.
            if analysis_result.start_column is not None:
                if analysis_result.start_column < 0:
                    raise ValueError(
                        f"start_column must be >= 0 "
                        f"(actual:{analysis_result.start_column})")
                encoded_str += f",col={analysis_result.start_column + 1}"
            if analysis_result.end_line is not None:
                if analysis_result.end_line < 0:
                    raise ValueError(
                        f"end_line must be >= 0 (actual:{analysis_result.end_line})")
                if analysis_result.start_line > analysis_result.end_line:
                    raise ValueError(
                        f"end_line must be >= start_line "
                        f"(actual: start:{analysis_result.start_line} "
                        f"end:{analysis_result.end_line})")
                encoded_str += f",endLine={analysis_result.end_line + 1}"
            if analysis_result.end_column is not None:
                if analysis_result.end_column < 0:
                    raise ValueError(
                        f"end_column must be >= 0 "
                        f"(actual:{analysis_result.end_column})")
                is_single_line = (
                    analysis_result.end_line is None
                    or analysis_result.start_line == analysis_result.end_line
                )
                if (
                    is_single_line
                    and analysis_result.start_column is not None
                    and analysis_result.start_column > analysis_result.end_column
                ):
                    raise ValueError(
                        f"end_column must be >= start_column if single line "
                        f"(actual: start:{analysis_result.start_column} "
                        f"end:{analysis_result.end_column})")
                encoded_str += f",endColumn={analysis_result.end_column + 1}"
        if analysis_result.title is not None:
            encoded_str += f",title={self._encode_property_str(analysis_result.title)}"
        encoded_str += f"::{self._encode_data_str(analysis_result.message)}"
        return encoded_str

    def _encode_severity(self, severity:Severity):
        """Encode severity enum into GitHub Annotation string."""
        SEVERITY_STRINGIFY_DICT = {
            Severity.ERROR: 'error',
            Severity.WARNING: 'warning',
            Severity.NOTICE: 'notice',
            Severity.UNKNOWN: 'warning'
        }
        # Fallback default severity is 'warning'.
        return SEVERITY_STRINGIFY_DICT.get(severity, 'warning')

    def _encode_property_str(self, src:str) -> str:
        """Encode as property string of GitHub workflow."""
        PROPERTY_ESCAPE_DICT = {
            '%': '%25',
            '\n': '%0A',
            '\r': '%0D',
            ',': '%2C',
            ':': '%3A'
        }
        return self._escape_by_dict(src, PROPERTY_ESCAPE_DICT)

    def _encode_data_str(self, src:str) -> str:
        """Encode as property string of GitHub workflow."""
        PROPERTY_ESCAPE_DICT = {
            '%': '%25',
            '\n': '%0A',
            '\r': '%0D',
        }
        return self._escape_by_dict(src, PROPERTY_ESCAPE_DICT)

    def _escape_by_dict(self, src: str, escape_dict) -> str:
        """Escape given str by escape_dict."""
        re_obj = re.compile("|".join(re.escape(key) for key in escape_dict))
        return re_obj.sub(lambda m: escape_dict[m.group(0)], src)

    def _normalize_dir(self, dir: str) -> str:
        """Normalize given dir string.

        * Path delimiters are unified into '/'
        * Starting with '/' for absolute path, even if for Windows path ('/C:/foo/bar/')
        * Ending with '/'
        """
        path = PureWindowsPath(dir)
        normalized_dir = path.as_posix()
        if path.is_absolute() and not normalized_dir.startswith('/'):
            normalized_dir = '/' + normalized_dir
        return normalized_dir.rstrip('/') + '/'

    def _resolve_as_project_root_relative_path(self, path: str) -> str:
        """Resolve path as project root relative if project root dir is specified."""
        if self._normalized_project_root_dir is None:
            return path
        return path.removeprefix(self._normalized_project_root_dir)
