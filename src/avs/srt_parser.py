def parse_srt(path):
    transcriptions = []
    with open(path, "r") as reader:
        contents = reader.read().split("\n\n")

        for i in range(0, len(contents)):
            # those are the raw timestamp pieces. Index 0
            # represents id (unused), index 1 represents the 
            # timestamp, which is processed using the process_timestamp_str func
            # last index represents the content itself
            current = contents[i].split("\n")
            current_timestamp = process_timestamp_str(current[1])

            if i == len(contents) - 1:
                transcriptions.append({
                    "start": current_timestamp[0],
                    "end": current_timestamp[1],
                    "text": current[2],
                    "is_silence": False
                })
                break

            next = contents[i + 1].split("\n")
            next_timestamp = process_timestamp_str(next[1])


            insert_silence = False
            # subtract next's start timestamp in ms from current's end timestamp also in ms
            delta = to_milliseconds(next_timestamp[0]) - to_milliseconds(current_timestamp[1])
            print("Delta is ", delta, " MS")
            if delta >= 1500:
                insert_silence = True

            transcriptions.append({
                "start": current_timestamp[0],
                "end": current_timestamp[1],
                "text": current[2],
                "is_silence": False
            })
            
            if insert_silence:
                transcriptions.append({
                    "start": current_timestamp[1],
                    "end": next_timestamp[0],
                    "is_silence": True
                })

    return transcriptions

def process_timestamp_str(timestamp_str):
    parts = timestamp_str.split(" --> ")

    return tuple(map(get_time_units, parts))

def get_time_units(timestamp_part_str):
    units = timestamp_part_str.split(":")
    secs_and_ms_units = units[2].split(",")
    return {
            "hour": int(units[0]),
            "minute": int(units[1]),
            "second": int(secs_and_ms_units[0]),
            "millisecond": int(secs_and_ms_units[1])
    }

def to_milliseconds(timestamp_dict):
    conversion_factors = {
        "hour": 3600000,       # 1 hour = 3600000 milliseconds
        "minute": 60000,       # 1 minute = 60000 milliseconds
        "second": 1000,        # 1 second = 1000 milliseconds
        "millisecond": 1       # 1 millisecond = 1 millisecond (no conversion needed)
    }

    return sum(value * conversion_factors.get(key, 0) for key, value in timestamp_dict.items())


# if __name__ == "__main__":
#     parse_srt("./resources/transcriptions/yeast.srt")
