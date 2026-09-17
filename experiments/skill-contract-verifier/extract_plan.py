#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import pathlib
import re

STEP_RE = re.compile(r"^- \[[ xX]\] \*\*Step (\d+):.*\*\*$")
UNITTEST_DISCOVER_RE = re.compile(r"(?:^|\s)python3\s+-m\s+unittest\s+discover(?:\s|$)")


def canonical_json(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"


def is_testcase_base(base):
    return (
        isinstance(base, ast.Attribute)
        and isinstance(base.value, ast.Name)
        and base.value.id == "unittest"
        and base.attr == "TestCase"
    ) or (isinstance(base, ast.Name) and base.id == "TestCase")


def parse_steps(lines):
    starts = []
    for index, line in enumerate(lines, start=1):
        match = STEP_RE.match(line)
        if match:
            starts.append((index, int(match.group(1))))
    steps = []
    for pos, (start_line, number) in enumerate(starts):
        end_line = starts[pos + 1][0] - 1 if pos + 1 < len(starts) else len(lines)
        steps.append({"number": number, "start_line": start_line, "end_line": end_line})
    return steps


def fenced_blocks(lines, step):
    blocks = []
    line_no = step["start_line"] + 1
    while line_no <= step["end_line"]:
        raw = lines[line_no - 1]
        if raw.startswith("```") and raw.strip() != "```":
            language = raw.strip()[3:].strip().lower()
            fence_line = line_no
            content = []
            line_no += 1
            content_start = line_no
            while line_no <= step["end_line"] and lines[line_no - 1].strip() != "```":
                content.append(lines[line_no - 1])
                line_no += 1
            if line_no <= step["end_line"]:
                blocks.append(
                    {
                        "language": language,
                        "fence_line": fence_line,
                        "content_start_line": content_start,
                        "content_end_line": line_no - 1,
                        "lines": content,
                    }
                )
        line_no += 1
    return blocks


def extract_witnesses(block):
    if block["language"] not in {"python", "py"}:
        return []
    source = "\n".join(block["lines"]) + "\n"
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    witnesses = []
    base_line = block["content_start_line"] - 1
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            witnesses.append(
                {
                    "name": node.name,
                    "form": "module_function",
                    "discoverable": False,
                    "span": {
                        "start_line": base_line + node.lineno,
                        "end_line": base_line + node.end_lineno,
                    },
                }
            )
        elif isinstance(node, ast.ClassDef) and any(is_testcase_base(base) for base in node.bases):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name.startswith("test_"):
                    witnesses.append(
                        {
                            "name": child.name,
                            "form": "unittest_testcase_method",
                            "discoverable": True,
                            "span": {
                                "start_line": base_line + child.lineno,
                                "end_line": base_line + child.end_lineno,
                            },
                        }
                    )
    return sorted(witnesses, key=lambda item: (item["span"]["start_line"], item["name"]))


def extract_payload(source_bytes):
    text = source_bytes.decode("utf-8")
    lines = text.splitlines()
    steps = parse_steps(lines)
    relations = []
    for index, consumer in enumerate(steps):
        if index == 0:
            continue
        producer = steps[index - 1]
        if consumer["number"] != producer["number"] + 1:
            continue
        producer_blocks = fenced_blocks(lines, producer)
        witnesses = []
        for block in producer_blocks:
            witnesses.extend(extract_witnesses(block))
        for block in fenced_blocks(lines, consumer):
            for offset, command in enumerate(block["lines"]):
                if UNITTEST_DISCOVER_RE.search(command.strip()):
                    relations.append(
                        {
                            "kind": "TDD_RUNNER_WITNESS",
                            "producer_step": {
                                "number": producer["number"],
                                "span": {
                                    "start_line": producer["start_line"],
                                    "end_line": producer["end_line"],
                                },
                            },
                            "consumer_step": {
                                "number": consumer["number"],
                                "span": {
                                    "start_line": consumer["start_line"],
                                    "end_line": consumer["end_line"],
                                },
                            },
                            "runner": {
                                "kind": "python_unittest_discover",
                                "command": command.strip(),
                                "span": {
                                    "start_line": block["content_start_line"] + offset,
                                    "end_line": block["content_start_line"] + offset,
                                },
                            },
                            "witnesses": witnesses,
                        }
                    )
    return {
        "schema_version": 1,
        "source": {
            "bytes": len(source_bytes),
            "sha256": hashlib.sha256(source_bytes).hexdigest(),
        },
        "relations": relations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=pathlib.Path)
    args = parser.parse_args()
    payload = extract_payload(args.source.read_bytes())
    print(canonical_json(payload), end="")


if __name__ == "__main__":
    main()
