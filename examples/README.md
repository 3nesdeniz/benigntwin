# Examples

| File | What it is |
| --- | --- |
| `pairs.jsonl` | Six matched pairs, each in English and Turkish (24 rows). Small enough to read in full; use it to try the commands, not to draw conclusions. |
| `my_detector.py` | A custom detector as a plain Python function. |

```bash
injectbench validate --dataset examples/pairs.jsonl
injectbench evaluate --dataset examples/pairs.jsonl --detector heuristic
injectbench evaluate --dataset examples/pairs.jsonl --detector python:examples/my_detector.py:detect
```

The second pair shows why pairs matter: both rows mention the system prompt, and only one of them is an attack.
