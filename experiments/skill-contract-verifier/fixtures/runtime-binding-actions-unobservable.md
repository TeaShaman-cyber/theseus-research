# Synthetic GitHub Actions unknown producer

```yaml
name: unknown-producer
on: workflow_dispatch
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - name: prepare
        run: |
          echo prepare
      - name: consume
        run: |
          python "$BUILD_ROOT/tool.py"
```
