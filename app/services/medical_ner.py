import re
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class MedicalNER:
    def __init__(self):
        self.nlp = None
        self._initialize_spacy()
        
        # Medical abbreviations dictionary
        self.medical_abbreviations = {
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'rr': 'respiratory rate',
            'temp': 'temperature',
            'bmi': 'body mass index',
            'cbc': 'complete blood count',
            'wbc': 'white blood cells',
            'rbc': 'red blood cells',
            'hgb': 'hemoglobin',
            'hct': 'hematocrit',
            'pt': 'prothrombin time',
            'inr': 'international normalized ratio',
            'ldl': 'low-density lipoprotein',
            'hdl': 'high-density lipoprotein',
            'mi': 'myocardial infarction',
            'chf': 'congestive heart failure',
            'copd': 'chronic obstructive pulmonary disease',
            'dm': 'diabetes mellitus',
            'htn': 'hypertension'
        }
    
    def _initialize_spacy(self):
        """Initialize spaCy with fallback if model not available"""
        try:
            import spacy
            self.nlp = spacy.load(settings.SPACY_MODEL)
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning(f"spaCy model {settings.SPACY_MODEL} not found. Using fallback NER.")
            self.nlp = None
        except ImportError:
            logger.warning("spaCy not installed. Using fallback NER.")
            self.nlp = None
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[Dict]]:
        """Extract medical entities from text"""
        entities = {
            'medications': self._extract_medications(text),
            'conditions': self._extract_conditions(text),
            'lab_results': self._extract_lab_results(text),
            'vital_signs': self._extract_vital_signs(text),
            'dates': self._extract_dates(text),
            'measurements': self._extract_measurements(text)
        }
        
        return entities
    
    def _extract_medications(self, text: str) -> List[Dict]:
        """Extract medication information using regex patterns"""
        medications = []
        
        # Enhanced medication patterns
        patterns = [
            r'(\b[A-Z][a-z]+\b)\s*(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|tablet|cap)s?)',
            r'(\b(?:Lisinopril|Metformin|Atorvastatin|Aspirin|Amoxicillin|Ibuprofen)\b.*?\d+.*?(?:mg|mcg))',
            r'Medication:\s*([^,\n]+?)\s*(\d+.*?)(?=\n|$)',
            r'Prescribed:\s*([^,\n]+?)\s*(\d+.*?)(?=\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medications.append({
                    'name': match.group(1).strip() if match.groups() > 1 else match.group(0),
                    'dosage': match.group(2).strip() if match.groups() > 1 else 'Unknown',
                    'text': match.group(0)
                })
        
        return medications
    
    def _extract_conditions(self, text: str) -> List[Dict]:
        """Extract medical conditions"""
        conditions = []
        
        # Common medical conditions pattern
        condition_patterns = [
            r'\b(hypertension|diabetes|asthma|arthritis|migraine|depression|anxiety)\b',
            r'\b(heart disease|kidney disease|liver disease|lung disease)\b',
            r'Diagnosis:\s*([^\n]+)',
            r'Condition:\s*([^\n]+)'
        ]
        
        for pattern in condition_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                conditions.append({
                    'condition': match.group(1) if match.groups() > 0 else match.group(0),
                    'label': 'CONDITION',
                    'text': match.group(0)
                })
        
        return conditions
    
    def _extract_lab_results(self, text: str) -> List[Dict]:
        """Extract laboratory results"""
        lab_results = []
        
        # Enhanced lab test patterns
        patterns = [
            r'(\w+)\s*:\s*([\d.]+)\s*(mg/dL|g/dL|mmol/L|%|U/L)?\s*(?:\(.*?(\d+)\s*-\s*(\d+).*?\))?',
            r'(\w+)\s+([\d.]+)\s*(mg/dL|g/dL|mmol/L|%|U/L)',
            r'(Glucose|Cholesterol|Hemoglobin|WBC|RBC)\s*:?\s*([\d.]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                lab_results.append({
                    'test': match.group(1),
                    'value': match.group(2),
                    'unit': match.group(3) or '',
                    'normal_range': f"{match.group(4)}-{match.group(5)}" if match.group(4) and match.group(5) else 'Unknown'
                })
        
        return lab_results
    
    def _extract_vital_signs(self, text: str) -> List[Dict]:
        """Extract vital signs"""
        vital_signs = []
        
        # Blood pressure pattern
        bp_pattern = r'blood pressure:?\s*(\d+)\s*/\s*(\d+)\s*(mmHg)?'
        bp_matches = re.finditer(bp_pattern, text, re.IGNORECASE)
        for match in bp_matches:
            vital_signs.append({
                'type': 'blood_pressure',
                'systolic': match.group(1),
                'diastolic': match.group(2),
                'unit': match.group(3) or 'mmHg'
            })
        
        # Heart rate pattern
        hr_pattern = r'heart rate:?\s*(\d+)\s*(bpm)?'
        hr_matches = re.finditer(hr_pattern, text, re.IGNORECASE)
        for match in hr_matches:
            vital_signs.append({
                'type': 'heart_rate',
                'value': match.group(1),
                'unit': match.group(2) or 'bpm'
            })
        
        return vital_signs
    
    def _extract_dates(self, text: str) -> List[Dict]:
        """Extract dates using regex patterns"""
        dates = []
        
        date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'Date:\s*([^\n]+)'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append({
                    'date': match.group(1) if match.groups() > 0 else match.group(0),
                    'text': match.group(0)
                })
        
        return dates
    
    def _extract_measurements(self, text: str) -> List[Dict]:
        """Extract various measurements"""
        measurements = []
        pattern = r'(\d+(?:\.\d+)?)\s*(kg|lb|cm|in|years?|y/o|cm|m)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            measurements.append({
                'value': match.group(1),
                'unit': match.group(2),
                'text': match.group(0)
            })
        return measurements
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations in text"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.medical_abbreviations:
                expanded_words.append(f"{word} ({self.medical_abbreviations[clean_word]})")
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)

medical_ner = MedicalNER()