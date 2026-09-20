def collect_normalized_topics(items):
    return sorted({
        entry["name"].strip().lower()
        for entry in items
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and entry["name"].strip()
    })
