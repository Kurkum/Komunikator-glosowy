import logging
import threading
import time
import functools
import datetime
import ConversationHistory as ch

# decorator is a cool way of timing the ongoing task, however you can't read global variables in it
# is there any other way of adding that time to time_history? i suppose not
def timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        elapsedTime = time.time() - startTime

        formatted_time = int(elapsedTime*1000)/1000

        print('function [{}] finished in {} s'.format(
            func.__name__, formatted_time))
    return newfunc


# global conversation history object
conversationHistoryController = ch.ConversationHistory()

def sample_conversation(x):
    startTime = time.time()
    conversation = conversationHistoryController.newConversation()
    for i in range(x):
        print(i)
    elapsedTime = time.time() - startTime
    formatted_time = int(elapsedTime * 1000) / 1000
    conversation["duration"] = formatted_time
    conversationHistoryController.addConversation(conversation)

if __name__ == "__main__":
    threadVar = threading.Thread(target=sample_conversation, args=(100000,))
    threadVar.start()
    threadVar.join()
    conversationHistoryController.readConversationHistory()

