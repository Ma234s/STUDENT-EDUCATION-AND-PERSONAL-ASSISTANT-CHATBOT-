import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from app import Config
import json
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processor with required models"""
        try:
            self.nlp = spacy.load(Config.SPACY_MODEL)
        except OSError:
            spacy.cli.download(Config.SPACY_MODEL)
            self.nlp = spacy.load(Config.SPACY_MODEL)
        
        self.sia = SentimentIntensityAnalyzer()
        
        # Load intent patterns
        self.intent_patterns = self._load_intent_patterns()
        
    def _load_intent_patterns(self):
        """Load intent recognition patterns from JSON file"""
        try:
            with open('app/nlp/intent_patterns.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Intent patterns file not found. Using default patterns.")
            return {
                "academic_query": ["how to", "explain", "what is", "define"],
                "task_management": ["create task", "add task", "remind me", "schedule"],
                "emotional_support": ["feeling", "stressed", "worried", "anxious"],
                "time_management": ["organize", "plan", "schedule", "manage time"],
                "study_technique": ["study method", "learn better", "memorize", "understand"]
            }

    def process_text(self, text, context=None):
        """
        Process input text and return structured information
        
        Args:
            text (str): Input text from user
            context (str, optional): Conversation context
            
        Returns:
            dict: Processed information including intent, entities, sentiment
        """
        doc = self.nlp(text)
        
        # Basic NLP analysis
        result = {
            'intent': self.detect_intent(text, context),
            'entities': self.extract_entities(doc),
            'sentiment': self.analyze_sentiment(text),
            'tokens': [token.text for token in doc],
            'pos_tags': [(token.text, token.pos_) for token in doc],
            'noun_phrases': [chunk.text for chunk in doc.noun_chunks]
        }
        
        return result
    
    def detect_intent(self, text, context=None):
        """
        Detect the intent of the user's message
        
        Args:
            text (str): Input text
            context (str, optional): Current conversation context
            
        Returns:
            dict: Intent information including type and confidence
        """
        text = text.lower()
        matched_intents = {}
        
        # Check against patterns
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text:
                    score += 1
            if score > 0:
                matched_intents[intent] = score / len(patterns)
        
        # If no intent matched, use context or default to general query
        if not matched_intents:
            return {
                'type': context or 'general_query',
                'confidence': 0.5
            }
        
        # Get the intent with highest confidence
        best_intent = max(matched_intents.items(), key=lambda x: x[1])
        return {
            'type': best_intent[0],
            'confidence': best_intent[1]
        }
    
    def extract_entities(self, doc):
        """
        Extract named entities and key information from text
        
        Args:
            doc: spaCy Doc object
            
        Returns:
            dict: Extracted entities and information
        """
        entities = {
            'dates': [],
            'times': [],
            'subjects': [],
            'named_entities': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['DATE', 'TIME']:
                entities['dates'].append({
                    'text': ent.text,
                    'label': ent.label_
                })
            elif ent.label_ == 'SUBJECT':
                entities['subjects'].append(ent.text)
            else:
                entities['named_entities'].append({
                    'text': ent.text,
                    'label': ent.label_
                })
        
        return entities
    
    def analyze_sentiment(self, text):
        """
        Perform sentiment analysis on text
        
        Args:
            text (str): Input text
            
        Returns:
            dict: Sentiment analysis results
        """
        # Use VADER for sentiment analysis
        vader_scores = self.sia.polarity_scores(text)
        
        # Use TextBlob for additional analysis
        blob = TextBlob(text)
        
        return {
            'compound': vader_scores['compound'],
            'positive': vader_scores['pos'],
            'negative': vader_scores['neg'],
            'neutral': vader_scores['neu'],
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def get_response_type(self, intent, sentiment):
        """
        Determine appropriate response type based on intent and sentiment
        
        Args:
            intent (dict): Intent information
            sentiment (dict): Sentiment analysis results
            
        Returns:
            str: Response type identifier
        """
        if sentiment['compound'] < -0.5:
            return 'emotional_support'
        elif intent['type'] == 'academic_query':
            return 'academic_explanation'
        elif intent['type'] == 'task_management':
            return 'task_creation'
        else:
            return 'general_response'

# Example usage
if __name__ == '__main__':
    processor = NLPProcessor()
    text = "I'm feeling stressed about my upcoming math exam next week"
    result = processor.process_text(text)
    print(json.dumps(result, indent=2)) 