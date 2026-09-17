# Synthetic GitHub Actions process-local binding

```yaml
name: process-local
on: workflow_dispatch
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: produce
        run: |
          export BUILD_ROOT="$PWD/src"
      - name: consume
        run: |
          python "$BUILD_ROOT/tool.py"
```
