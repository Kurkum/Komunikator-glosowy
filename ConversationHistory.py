import json


class ConversationHistory:
    def __init__(self):
        self.conversationContainer = []

    def newConversation(self):
        conversation = dict.fromkeys(["id", "source", "target", "duration", "status", "messages-sent",
                                     "messages-sent-by-source", "messages-sent-by-target", "breaks",
                                     "breaks-taken-by-source", "breaks-taken-by-target"])
        return conversation

    def readConversationHistory(self):
        print(self.conversationContainer)

    def getConversationHistory(self):
        return self.conversationContainer

    def addConversation(self, conversation):
        conversationContainerLength = len(self.conversationContainer) + 1
        conversation["id"] = conversationContainerLength
        self.conversationContainer.append(conversation)

    def clearConversationHistory(self):
        self.conversationContainer = []

    def getJSON(self):
        return json.dumps(self.conversationContainer)

    def printJSON(self):
        print(json.dumps(self.conversationContainer, indent=4))

    def saveConversationHistoryToFile(self):
        file = open("conversation_history.json", "w")
        file.write(self.getJSON())
        file.close()

    def readConversationHistoryFromFile(self):
        file = open("conversation_history.json", "r")
        return file.read()

    def prettifyConversation(self, conversation):
        output = ""
        for key, value in conversation.items():
            output += str(key) + " - " + str(value) + "\n"
        return output

if __name__ == '__main__':
    convHis = ConversationHistory()
    conversation = {
        "id": 1,
        "source": "192.168.0.1",
        "target": "192.168.0.2",
        "duration": "00:23:47:09",
        "status": "ended-properly",
        "messages-sent": 13,
        "messages-sent-by-source": 7,
        "messages-sent-by-target": 6,
        "breaks": 0,
        "breaks-taken-by-source": 0,
        "breaks-taken-by-target": 0
    }
    conversationSub = {
        "id": 2,
        "source": "192.168.0.4",
        "target": "192.168.0.1",
        "duration": "00:13:47:09",
        "status": "ended-properly",
        "messages-sent": 13,
        "messages-sent-by-source": 7,
        "messages-sent-by-target": 6,
        "breaks": 1,
        "breaks-taken-by-source": 1,
        "breaks-taken-by-target": 1
    }
    convHis.readConversationHistory()
    convHis.addConversation(conversation)
    convHis.addConversation(conversationSub)
    convHis.readConversationHistory()
    convHis.printJSON()
