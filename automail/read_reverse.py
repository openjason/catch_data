import os
import collections

def read_reverse(filename):
    f = open(filename)
    f.seek(0, 2)
    last_position = f.tell()

    while True:
        line = f.readline()
        current_position = f.tell()
        i = 1
        while current_position == last_position:
            if len(line) == current_position:
                yield line
                return
            i += 0.5
            f.seek(max(int(-72 * i), -current_position), 1)
            line = f.readline()
            current_position = f.tell()

        while current_position != last_position:
            line = f.readline()
            current_position = f.tell()
            print(line)

        yield line
        last_position = last_position - len(line)
        f.seek(max(-72, -last_position) - len(line), 1)

def tail(filename, n=10):
    'Return the last n lines of a file'
    return collections.deque(open(filename), n)


if __name__ == "__main__":

#    read_reverse("e:\\test\\automail.log")
    f = "e:\\test\\automail.log"
    fl = tail(f,30)
    # f=open("e:\\test\\automail.log",'r')
    #
    # a=f.readlines()
    #
    for i in range(len(fl)-1,0,-1):
        print(fl[i])

    print("ok?")
