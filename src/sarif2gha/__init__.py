# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import argparse
import sys
from pathlib import Path

from sarif2gha.conversion_context import ConversionContext
from sarif2gha.github_annotation_encoder import GitHubAnnotationEncoder
from sarif2gha.sarif_loader import SarifLoader
from sarif2gha.stdout_writer import StdoutWriter

_EXIT_CODE_OK = 0
_EXIT_CODE_CONVERSION_ERROR = 1


def _parse_commandline_arguments() -> argparse.Namespace:
    """Parse CLI arguments."""
    argparser = argparse.ArgumentParser(
        description='Convert from SARIF into GitHub annotation styled texts.'
    )

    argparser.add_argument(
        '--project-root-dir',
        required=False,
        type=Path,
        help='Project root dir path to resolve paths in SARIF into relative path.'
    )

    argparser.add_argument(
        'sarif_path',
        nargs=1,
        type=Path,
        help='Input SARIF path.'
    )

    return argparser.parse_args()

def main() -> int:
    """Entry point to sarif2gha."""
    args = _parse_commandline_arguments()
    loader = SarifLoader()
    encoder = GitHubAnnotationEncoder(args.project_root_dir)
    writer = StdoutWriter()
    context = ConversionContext(args.sarif_path[0], loader, encoder, writer)
    conversion_result = context.run()
    if conversion_result is None:
        return _EXIT_CODE_OK
    sys.stderr.write(f"{conversion_result}\n")
    return _EXIT_CODE_CONVERSION_ERROR
