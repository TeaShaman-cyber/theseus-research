# Synthetic GitHub Actions transported binding

```yaml
name: github-env
on: workflow_dispatch
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: produce
        run: |
          echo "BUILD_ROOT=$PWD/src" >> "$GITHUB_ENV"
      - name: consume
        run: |
          python "$BUILD_ROOT/tool.py"
```
