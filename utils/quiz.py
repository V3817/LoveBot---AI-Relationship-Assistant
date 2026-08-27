class QuizManager:
    def __init__(self):
        self.questions = [
            {
                "id": 1,
                "text": "How do you prefer to receive affection?",
                "options": [
                    "Through words of affirmation",
                    "Through physical touch",
                    "Through acts of service",
                    "Through receiving gifts",
                    "Through quality time"
                ],
                "category": "love_language"
            },
            {
                "id": 2,
                "text": "When facing relationship conflicts, you typically:",
                "options": [
                    "Try to find a compromise immediately",
                    "Need time to process before discussing",
                    "Prefer to address issues head-on",
                    "Seek advice from others first",
                    "Try to avoid the conflict"
                ],
                "category": "conflict_style"
            },
            {
                "id": 3,
                "text": "In social situations, you usually:",
                "options": [
                    "Enjoy being the center of attention",
                    "Prefer one-on-one conversations",
                    "Like to observe before engaging",
                    "Feel energized by group activities",
                    "Prefer small, intimate gatherings"
                ],
                "category": "social_style"
            }
        ]
        
    def get_questions(self):
        """Return all quiz questions"""
        return self.questions
        
    def analyze_results(self, responses):
        """Analyze quiz responses and return personality insights"""
        insights = {
            "love_language": "",
            "conflict_style": "",
            "social_style": "",
            "summary": ""
        }
        
        # Analyze love language
        if 1 in responses:
            love_languages = ["Words of Affirmation", "Physical Touch", "Acts of Service", 
                            "Gift Giving", "Quality Time"]
            insights["love_language"] = love_languages[responses[1]]
            
        # Analyze conflict style
        if 2 in responses:
            conflict_styles = ["Compromising", "Processing", "Confrontational", 
                             "Consulting", "Avoiding"]
            insights["conflict_style"] = conflict_styles[responses[2]]
            
        # Analyze social style
        if 3 in responses:
            social_styles = ["Extroverted", "Personal", "Observant", 
                           "Social", "Intimate"]
            insights["social_style"] = social_styles[responses[3]]
            
        # Generate summary
        insights["summary"] = f"""Based on your responses, your primary love language is {insights['love_language']}.
When it comes to handling conflicts, you tend to take a {insights['conflict_style'].lower()} approach.
In social situations, you are more {insights['social_style'].lower()}.
This combination suggests you value {self._get_value_statement(insights)}.
"""
        return insights
        
    def _get_value_statement(self, insights):
        """Generate a personalized value statement"""
        value_statements = {
            "Words of Affirmation": "clear communication and emotional expression",
            "Physical Touch": "physical connection and presence",
            "Acts of Service": "practical demonstrations of care",
            "Gift Giving": "thoughtful gestures and symbolic expressions of love",
            "Quality Time": "dedicated attention and shared experiences"
        }
        return value_statements.get(insights["love_language"], "authentic connections")
