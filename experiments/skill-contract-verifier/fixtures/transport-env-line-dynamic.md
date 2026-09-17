# Synthetic transport boundary: dynamic source

```yaml
jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - name: produce
        run: |
          PAYLOAD="$(compute_payload)"
          echo "PAYLOAD=$PAYLOAD" >> "$GITHUB_ENV"
      - name: consume
        run: printf '%s\n' "$PAYLOAD"
```
