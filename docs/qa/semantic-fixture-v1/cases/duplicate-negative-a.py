def missing_topics(expected, observed):
    expected_set = set(expected)
    observed_set = set(observed)
    return sorted(expected_set - observed_set)
