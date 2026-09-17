#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import pathlib
import re

STEP_RE = re.compile(r"^- \[[ xX]\] \*\*Step (\d+):.*\*\*$")
UNITTEST_DISCOVER_RE = re.compile(r"(?:^|\s)python3\s+-m\s+unittest\s+discover(?:\s|$)")
VAR_USE_RE = re.compile(r"\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))")
EXPORT_ASSIGN_RE = re.compile(r"^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=")


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



def workflow_yaml_blocks(lines):
    whole_file = {"start_line": 0, "end_line": len(lines)}
    return [
        block
        for block in fenced_blocks(lines, whole_file)
        if block["language"] in {"yaml", "yml"}
    ]


def indentation(raw):
    return len(raw) - len(raw.lstrip(" "))


def parse_run_script(item_lines, item_start_line):
    for offset, raw in enumerate(item_lines):
        match = re.match(r"^\s*(?:-\s+)?run:\s*(.*)$", raw)
        if not match:
            continue
        value = match.group(1).strip()
        run_line = item_start_line + offset
        if value.startswith("|") or value.startswith(">"):
            run_indent = indentation(raw)
            script = []
            for child_offset, child in enumerate(item_lines[offset + 1 :], start=offset + 1):
                if child.strip() and indentation(child) <= run_indent:
                    break
                if child.strip():
                    script.append(
                        {
                            "text": child.lstrip(),
                            "line": item_start_line + child_offset,
                        }
                    )
            return {"span": {"start_line": run_line, "end_line": script[-1]["line"] if script else run_line}, "lines": script}
        if value:
            return {
                "span": {"start_line": run_line, "end_line": run_line},
                "lines": [{"text": value, "line": run_line}],
            }
        return {"span": {"start_line": run_line, "end_line": run_line}, "lines": []}
    return None


def parse_actions_step_groups(block):
    rows = block["lines"]
    groups = []
    for steps_pos, raw in enumerate(rows):
        match = re.match(r"^(\s*)steps:\s*$", raw)
        if not match:
            continue
        steps_indent = len(match.group(1))
        starts = []
        list_indent = None
        pos = steps_pos + 1
        while pos < len(rows):
            candidate = rows[pos]
            if candidate.strip() and indentation(candidate) <= steps_indent:
                break
            item = re.match(r"^(\s*)-\s+", candidate)
            if item and len(item.group(1)) > steps_indent:
                current_indent = len(item.group(1))
                if list_indent is None:
                    list_indent = current_indent
                if current_indent == list_indent:
                    starts.append(pos)
            pos += 1
        if not starts:
            continue
        steps = []
        boundary = pos
        for index, start in enumerate(starts, start=1):
            end = starts[index] if index < len(starts) else boundary
            item_lines = rows[start:end]
            global_start = block["content_start_line"] + start
            global_end = block["content_start_line"] + end - 1
            steps.append(
                {
                    "index": index,
                    "span": {"start_line": global_start, "end_line": global_end},
                    "run": parse_run_script(item_lines, global_start),
                }
            )
        groups.append(steps)
    return groups


def run_variable_uses(run):
    uses = []
    seen = set()
    if not run:
        return uses
    for row in run["lines"]:
        for match in VAR_USE_RE.finditer(row["text"]):
            name = match.group(1) or match.group(2)
            if name in {"GITHUB_ENV", "PWD"} or name in seen:
                continue
            seen.add(name)
            uses.append({"binding": name, "span": {"start_line": row["line"], "end_line": row["line"]}})
    return uses


def actions_producer_for_binding(run, binding):
    if not run:
        return None, {"kind": "unknown"}
    for row in run["lines"]:
        text = row["text"]
        line_span = {"start_line": row["line"], "end_line": row["line"]}
        if "$GITHUB_ENV" in text and ">>" in text:
            before_redirect = text.split(">>", 1)[0]
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(binding)}=", before_redirect):
                return (
                    {"kind": "github_env_write", "boundary": "github_actions_run_step", "span": line_span},
                    {"kind": "github_env_next_steps"},
                )
        export_match = EXPORT_ASSIGN_RE.match(text)
        if export_match and export_match.group(1) == binding:
            return (
                {"kind": "shell_export", "boundary": "github_actions_run_step", "span": line_span},
                {"kind": "process_local"},
            )
    return None, {"kind": "unknown"}


def extract_actions_runtime_relations(lines):
    relations = []
    for block in workflow_yaml_blocks(lines):
        for steps in parse_actions_step_groups(block):
            for pos, consumer_step in enumerate(steps):
                if pos == 0 or not consumer_step["run"]:
                    continue
                producer_step = steps[pos - 1]
                for use in run_variable_uses(consumer_step["run"]):
                    producer, transport = actions_producer_for_binding(producer_step["run"], use["binding"])
                    relations.append(
                        {
                            "kind": "RUNTIME_BINDING",
                            "binding": use["binding"],
                            "producer_step": {"index": producer_step["index"], "span": producer_step["span"]},
                            "consumer_step": {"index": consumer_step["index"], "span": consumer_step["span"]},
                            "producer": producer,
                            "transport": transport,
                            "consumer": {
                                "kind": "shell_variable_expansion",
                                "boundary": "github_actions_run_step",
                                "span": use["span"],
                            },
                        }
                    )
    return relations



def parse_supported_shell_literal(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw.startswith("'") and raw.endswith("'"):
        body = raw[1:-1]
        if "'" in body:
            return None
        return body
    if len(raw) >= 3 and raw.startswith("$'") and raw.endswith("'"):
        body = raw[2:-1]
        out = []
        index = 0
        escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", "'": "'"}
        while index < len(body):
            char = body[index]
            if char != "\\":
                out.append(char)
                index += 1
                continue
            index += 1
            if index >= len(body) or body[index] not in escapes:
                return None
            out.append(escapes[body[index]])
            index += 1
        return "".join(out)
    return None


def simple_github_env_write(run, binding):
    if not run:
        return None
    escaped = re.escape(binding)
    pattern = re.compile(
        rf"^\s*echo\s+[\"']{escaped}=\$(?:{escaped}|\{{{escaped}\}})[\"']\s*>>\s*[\"']?\$GITHUB_ENV[\"']?\s*$"
    )
    matches = [row for row in run["lines"] if pattern.match(row["text"])]
    return matches[0] if len(matches) == 1 else None


def source_semantics_for_binding(run, binding, before_line):
    if not run:
        return {"kind": "unknown"}
    escaped = re.escape(binding)
    assignment = re.compile(rf"^\s*{escaped}=(.*)$")
    candidates = []
    for row in run["lines"]:
        if row["line"] >= before_line:
            continue
        match = assignment.match(row["text"])
        if match:
            candidates.append((row, match.group(1)))
    if not candidates:
        return {"kind": "unknown"}
    row, raw = candidates[-1]
    value = parse_supported_shell_literal(raw)
    if value is None:
        return {"kind": "unknown", "span": {"start_line": row["line"], "end_line": row["line"]}}
    value_bytes = value.encode("utf-8")
    return {
        "kind": "literal_string",
        "bytes": len(value_bytes),
        "sha256": hashlib.sha256(value_bytes).hexdigest(),
        "contains_line_break": "\n" in value or "\r" in value,
        "span": {"start_line": row["line"], "end_line": row["line"]},
    }


def extract_actions_transport_relations(lines):
    relations = []
    for block in workflow_yaml_blocks(lines):
        for steps in parse_actions_step_groups(block):
            for pos, consumer_step in enumerate(steps):
                if pos == 0 or not consumer_step["run"]:
                    continue
                producer_step = steps[pos - 1]
                if not producer_step["run"]:
                    continue
                for use in run_variable_uses(consumer_step["run"]):
                    binding = use["binding"]
                    write = simple_github_env_write(producer_step["run"], binding)
                    if write is None:
                        continue
                    relations.append(
                        {
                            "kind": "TRANSPORT_BOUNDARY",
                            "binding": binding,
                            "producer_step": {"index": producer_step["index"], "span": producer_step["span"]},
                            "consumer_step": {"index": consumer_step["index"], "span": consumer_step["span"]},
                            "source_semantics": source_semantics_for_binding(
                                producer_step["run"], binding, write["line"]
                            ),
                            "encoding": {
                                "kind": "github_env_simple_line",
                                "span": {"start_line": write["line"], "end_line": write["line"]},
                            },
                            "consumer": {
                                "kind": "shell_variable_expansion",
                                "span": use["span"],
                            },
                        }
                    )
    return relations

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
    relations.extend(extract_actions_runtime_relations(lines))
    relations.extend(extract_actions_transport_relations(lines))
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
