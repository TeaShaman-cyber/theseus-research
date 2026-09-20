def _dump(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _load_valid_registry() -> tuple[dict[str, object] | None, list[str]]:
    try:
        document = load_registry(REGISTRY)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return None, [str(exc)]
    errors = validate_registry(document)
    return document, errors
