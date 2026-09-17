# Synthetic transport boundary: safe simple env line

```yaml
jobs:
  demo:
    runs-on: ubuntu-latest
    steps:
      - name: produce
        run: |
          PAYLOAD='SAFE'
          echo "PAYLOAD=$PAYLOAD" >> "$GITHUB_ENV"
      - name: consume
        run: printf '%s\n' "$PAYLOAD"
```
