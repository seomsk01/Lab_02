def count_events(events: list) -> int:
    return len(events)


def count_levels(events: list) -> dict:
    level_counts = {}

    for event in events:
        if event.level not in level_counts:
            level_counts[event.level] = 1

        else:
            level_counts[event.level] += 1

    return level_counts


def count_sources(events: list) -> dict:
    source_counts = {}

    for event in events:
        if event.source not in source_counts:
            source_counts[event.source] = 1

        else:
            source_counts[event.source] += 1

    return source_counts


def top5_errors(events: list) -> list[tuple[str, int]]:
    error_counts = {}

    for event in events:
        if event.level in ("ERROR", "CRITICAL"):
            if event.source not in error_counts:
                error_counts[event.source] = 1
            else:
                error_counts[event.source] += 1

    return sorted(
        error_counts.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]


def get_time(events: list) -> tuple:
    if not events:
        return None, None

    timestamps = [event.timestamp for event in events]

    return min(timestamps), max(timestamps)
