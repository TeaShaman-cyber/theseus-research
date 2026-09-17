- [ ] **Step 1: Write failing test**

```python
import unittest

class RuntimeContractTests(unittest.TestCase):
    def test_runtime_contract_files_exist(self):
        self.assertTrue(False)
```

- [ ] **Step 2: Run RED**

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```
