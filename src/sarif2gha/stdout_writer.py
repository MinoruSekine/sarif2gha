# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Copyright (C) 2026 Minoru Sekine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import sys


class StdoutWriter:
    def write(self, src_str: str):
        sys.stdout.write(f"{src_str}\n")
        # Flushing will help log processing by GitHub.
        sys.stdout.flush()

