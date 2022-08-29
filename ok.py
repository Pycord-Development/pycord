class AA:
    def __init__(self):
        print("AA")

class AB:
    def __init__(self):
        print("AB")

class BA(AB, AA):
    def __init__(self):
        super(AB, self).__init__()

test = BA()

import time
time.sleep(2)

print(BA)
