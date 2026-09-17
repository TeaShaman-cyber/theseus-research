# Synthetic transport boundary: newline semantic loss

```yaml
jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - name: produce
        run: |
          PAYLOAD=$'SAFE\nINJECTED=value'
          echo "PAYLOAD=$PAYLOAD" >> "$GITHUB_ENV"
      - name: consume
        run: printf '%s\n' "$PAYLOAD"
```
