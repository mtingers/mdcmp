# this file describes how to write a drum pattern in text format
# w = whole 4
# h = half 2
# q = quarter 1
# e = eigtht 0.5
# s = sixteenth 0.25
# t = thirty-second 0.125
# 0 = skip/0 value
# format: name|start-time-offset|note,note-additional-time,volume;...
# kick1|0|q,0,100;
# snare1|1|h,0,100;
import sys


def kick():
    data = "kick1|0|"
    for _ in range(100):
        data += "h,0,50;"
    return data


def floortom():
    data = "lowfloortom|0|"
    for _ in range(100):
        data += "w,0,100;"
    return data


def hat():
    data = "hat1|0|"
    for _ in range(200):
        data += "e,0,50;"
    return data


def snare():
    data = "snare1|1|;"
    for i in range(1, 100):
        if i % 8 == 0 and i > 0:
            data += "e,0,50;e,t,80;e,0,0;e,t,0;"
        else:
            data += "h,0,50;"
    return data


def main():
    gens = (kick, snare, hat, floortom)
    data = "\n".join([i() for i in gens])
    with open(sys.argv[1], "w") as fd:
        fd.write(data)


if __name__ == "__main__":
    main()
