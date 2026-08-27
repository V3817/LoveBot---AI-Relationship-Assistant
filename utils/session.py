class SessionManager:
    def __init__(self):
        self.max_history = 50  # Maximum number of messages to keep in history
        
    def trim_history(self, messages):
        """Trim message history to prevent session from growing too large"""
        if len(messages) > self.max_history:
            return messages[-self.max_history:]
        return messages
