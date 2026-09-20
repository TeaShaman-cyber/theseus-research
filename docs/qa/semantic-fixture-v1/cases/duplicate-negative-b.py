def added_release_tags(previous, current):
    previous_set = set(previous)
    current_set = set(current)
    return sorted(current_set - previous_set)
