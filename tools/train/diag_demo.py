"""Reads a DarkPlaces/Xonotic .dem and prints how evenly the server packets are spaced: each block is
int32 length, 3 floats of view angles and the message, which normally starts with svc_time (7)
and a float of server time.

Usage: python diag_demo.py <file.dem>
"""
import collections
import struct
import sys


def main():
    data = open(sys.argv[1], "rb").read()
    pos = data.index(b"\n") + 1          # the demo starts with the CD track line
    times = []
    while pos + 16 <= len(data):
        length = struct.unpack_from("<i", data, pos)[0]
        if length < 0 or pos + 16 + length > len(data):
            break
        message = data[pos + 16:pos + 16 + length]
        if len(message) >= 5 and message[0] == 7:
            times.append(struct.unpack_from("<f", message, 1)[0])
        pos += 16 + length
    steps = [round((b - a) * 1000, 1) for a, b in zip(times, times[1:])]
    print(f"{len(times)} packets with svc_time, {times[0]:.2f}..{times[-1]:.2f} s, "
          f"{len(times) / max(times[-1] - times[0], 1e-6):.1f} per second")
    print("most common steps (ms):", collections.Counter(steps).most_common(10))
    middle = len(steps) // 2
    print("steps in the middle:", steps[middle:middle + 60])


if __name__ == "__main__":
    main()
