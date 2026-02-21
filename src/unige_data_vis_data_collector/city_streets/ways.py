from unige_data_vis_data_collector.city_streets.way_segment import WaySegment


class Ways:
    _segments: dict[str, list[WaySegment]]

    def __init__(self):
        self._segments = {}

    def append(self, segment: WaySegment):
        if segment.name not in self._segments:
            self._segments[segment.name] = []

        if self._segments[segment.name]:
            print(f">>>>>>>>>>>>>>>>>> {segment.name}")
            for seg in self._segments[segment.name]:
                print(seg)
            print("==================")
            print(segment)
            print("<<<<<<<<<<<<<<<<<<")

        self._segments[segment.name].append(segment)
