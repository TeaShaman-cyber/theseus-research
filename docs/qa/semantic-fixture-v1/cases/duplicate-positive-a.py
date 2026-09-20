def normalized_topic_names(records):
    names = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        name = record.get("name")
        if isinstance(name, str) and name.strip():
            names.add(name.strip().lower())
    return sorted(names)
