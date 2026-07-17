import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Dict, Tuple
from utils.logger import setup_logger

logger = setup_logger("KeywordDetector")

class KeywordDetector:
    def __init__(self, keywords: List[str], phrases: List[str]):
        logger.info("Loading spaCy model (en_core_web_sm)...")
        try:
            # Load small english model. Disable heavy components we don't need for pure token matching.
            self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
            raise

        # We match on the "LEMMA" attribute to handle plurals and tenses (run, ran, running -> run)
        # We also want case-insensitivity, which lemmatization mostly handles, but LOWER is another option.
        # Lemmatization is better for our use case.
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LEMMA")
        
        self.keywords = keywords
        self.phrases = phrases
        self._add_patterns()
        
    def _add_patterns(self):
        """Adds keywords and phrases to the PhraseMatcher."""
        all_terms = self.keywords + self.phrases
        
        for term in all_terms:
            # Create a document for the term
            doc = self.nlp(term.lower())
            # Add to matcher with the original term as the match ID (string)
            self.matcher.add(term.lower(), [doc])
            
        logger.info(f"Loaded {len(all_terms)} keywords/phrases into matcher.")

    def detect(self, text: str) -> List[str]:
        """
        Takes a raw transcript string, lemmatizes it, and returns a list of detected keywords/phrases.
        """
        if not text:
            return []
            
        # Process the transcript
        doc = self.nlp(text.lower())
        
        # Find matches
        matches = self.matcher(doc)
        
        detected = []
        for match_id, start, end in matches:
            # match_id is a hash, we can get the string representation
            string_id = self.nlp.vocab.strings[match_id]
            detected.append(string_id)
            
        return detected
