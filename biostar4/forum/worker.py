
import time

def test(message):
    print ("*** channel: {}".format(message.channel))
    print ("*** content: {}".format(message.content))
    print ("*** sleep")
    time.sleep(1)
    print ("*** done")
