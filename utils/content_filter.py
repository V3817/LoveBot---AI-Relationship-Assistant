class ContentFilter:
    def __init__(self):
        self.blocked_words = {
            'explicit', 'nsfw', 'porn', 'xxx',
            # Add more blocked words as needed
        }
        
    def is_safe(self, content):
        """Basic content filtering"""
        content_lower = content.lower()
        
        # Check for blocked words
        for word in self.blocked_words:
            if word in content_lower:
                return False
                
        return True
