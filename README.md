# sarif2gha

Convert SARIF results into GitHub Actions log annotations.

## Samples

### Integrate with `microsoft/psscriptanalyzer-action`

```YAML
jobs:
  PSScriptAnalyzer:
    runs-on: windows-latest

    steps:
      - name: Check out
        uses: actions/checkout@v6
        with:
          persist-credentials: false

      - name: Run PSScriptAnalyzer
        uses: microsoft/psscriptanalyzer-action@v1.1
        with:
          path: .\
          recurse: true
          output: psscriptanalyzer.sarif

      - uses: astral-sh/setup-uv@v7.2.0

      - name: Run sarif2gha
        run: |
          uvx --from `
          git+https://github.com/MinoruSekine/sarif2gha.git@abbea6e `
          sarif2gha `
          --project-root-dir="${{ github.workspace }}" psscriptanalyzer.sarif
        shell: pwsh
```

## Screenshots

### GitHub Annotations from `psscriptanalyzer-action` via `sarif2gha`

![Screenshot with `psscriptanalyzer-action`](./doc/screenshot_psscriptanalyzeraction.png)
