# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import re

from sarif2gha.analysis_result import AnalysisResult, Severity


class GitHubAnnotationEncoder:
    """Encoder for GitHub Annotation style string from analysis data."""
    def encode(self, analysis_result: AnalysisResult) -> str:
        """Encode GitHub Annotation string from AnalysisResult instance."""
        encoded_str = f"::{self._encode_severity(analysis_result.severity)} "
        encoded_str += f"file={self._encode_property_str(analysis_result.file)}"
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
                encoded_str += f",endLine={analysis_result.end_line + 1}"
            if analysis_result.end_column is not None:
                if analysis_result.end_column < 0:
                    raise ValueError(
                        f"end_column must be >= 0 "
                        f"(actual:{analysis_result.end_column})")
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
