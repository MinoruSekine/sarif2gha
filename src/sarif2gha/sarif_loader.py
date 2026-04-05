# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
from dataclasses import dataclass
from pathlib import Path

from sarif2gha.analysis_result import AnalysisResult, Severity


@dataclass
class LoadSuccessData:
    """Data structure for successful load."""
    results: list[AnalysisResult]

@dataclass
class LoadFailureData:
    """Data structure for load failure."""
    message: str = ""

class SarifLoader:
    """Loads SARIF into list of internal data structures."""

    def load(self, sarif_path: Path) -> LoadSuccessData | LoadFailureData:
        """
        Loads SARIF into list of internal data structures.

        Args:
            sarif_path: SARIF file path to load.

        Returns:
            LoadSuccessData | LoadFailureData:
                A LoadSuccessData object if the sarif_path is loaded correctly,
                otherwise a LoadFailureData object containing details.
        """
        load_result = None
        try:
            with sarif_path.open(mode='r') as sarif_file:
                sarif_json = json.load(sarif_file)
        except Exception as e:
            load_result = LoadFailureData(message=f"Failed to open {sarif_path}: {e}")

        if not isinstance(load_result, LoadFailureData):
            # Parse error shouldn't be error, it may mean just "no messages".
            load_result = LoadSuccessData(results=[])
            match sarif_json:
                case {"runs": [*runs]}:
                    for run in runs:
                        rules_dict = self._parse_rules_in_run(run)
                        parsed_run = self._parse_each_run(run, rules_dict)
                        load_result.results += parsed_run
                case _:
                    # If no "runs" field, no messages available,
                    # but that may not be error. So returns just empty result.
                    pass

        return load_result

    def _parse_rules_in_run(self, run):
        """Parse rules in each item in "runs" field into dict."""
        rules_dict = {}
        match run:
            case {"tool": {"driver": {"rules": [*rules]}}}:
                for rule in rules:
                    match rule:
                        case {"id": rule_id}:
                            rules_dict[rule_id] = rule

        return rules_dict

    def _get_rule_short_desc(self, rules_dict, rule_id) -> str:
        """Returns short description of the specified rule."""
        rule = rules_dict.get(rule_id)
        if rule is not None:
            match rule:
                case {"shortDescription": {"text": text}}:
                    short_desc = text
                case _:
                    short_desc = rule_id
        else:
            short_desc = rule_id

        return short_desc

    def _parse_each_run(self, run, rules_dict) -> list[AnalysisResult]:
        """Parse each item in "runs" field of SARIF."""
        # Parse failure at each run may mean just "no messages there".
        parsed_run = []
        match run:
            case {"results": [*results]}:
                for result in results:
                    a_result = self._parse_each_result(result, rules_dict)
                    parsed_run += a_result

        return parsed_run

    def _parse_each_result(
        self,
        result,
        rules_dict
    ) -> list[AnalysisResult]:
        """Parse each items in "results" field of SARIF."""
        # Parse failure at each result may mean just "no messages there".
        parsed_result = []
        match result:
            case {
                "ruleId": rule_id,
                "message": {"text": message_text},
                "locations": [*locations]
            }:
                for location in locations:
                    match location:
                        case {
                            "physicalLocation": {
                                "artifactLocation": {"uri": uri}
                            } as physical_location
                        }:
                            parsed_phys_loc = AnalysisResult(
                                message=message_text,
                                title=self._get_rule_short_desc(rules_dict, rule_id),
                                file=self._convert_uri_to_file(uri),
                                severity=self._convert_level_to_severity(
                                    # In SARIF spec,
                                    # "level" should be fall back to warning
                                    # if no "level" exists.
                                    result.get("level", "warning")
                                )
                            )
                            match physical_location:
                                case {"region": region}:
                                    start_line = self._adjust_origin_sarif_to_0(
                                        # In SARIF spec,
                                        # omitting "startLine" means "head of file".
                                        region.get("startLine", 1)
                                    )
                                    parsed_phys_loc.start_line = start_line

                                    start_column = self._adjust_origin_sarif_to_0(
                                        region.get("startColumn")
                                    )
                                    parsed_phys_loc.start_column = start_column

                                    end_line = self._adjust_origin_sarif_to_0(
                                        region.get("endLine")
                                    )
                                    parsed_phys_loc.end_line = end_line

                                    end_column = self._adjust_origin_sarif_to_0(
                                        region.get("endColumn")
                                    )
                                    parsed_phys_loc.end_column = end_column
                            parsed_result.append(parsed_phys_loc)
        return parsed_result

    def _adjust_origin_sarif_to_0(self, sarif_value: int | None) -> int | None:
        """Adjust origin of line or column number in SARIF to 0-origin.

        Line and column in SARIF are 1-origin, but internal data are 0-origin.
        And SARIF can omit each line and/or column field(s).

        Args:
            sarif_value: Raw line or column value just loaded from SARIF, or None.

        Returns:
            int | None: 0-origin adjusted line or column value if sarif_value is int,
                        None if sarif_value is None.
        """
        return max(sarif_value - 1, 0) if isinstance(sarif_value, int) else None

    def _convert_level_to_severity(self, level: str) -> Severity:
        """Convert "level" string in SARIF into internal severity enum.

            Args:
                level: "level" string in SARIF.

            Returns:
                Severity: Severity enum corresponding to arg level.

            Note: In this implementation, unknown level will fallback to warning.
        """
        level_dict = {
            'none': Severity.NOTICE,
            'note': Severity.NOTICE,
            'warning': Severity.WARNING,
            'error': Severity.ERROR
        }
        return level_dict.get(level, Severity.WARNING)

    def _convert_uri_to_file(self, uri: str) -> str:
        """Convert "uri" field string to file path."""
        # TODO: Convert to project-root relative path.
        return uri
