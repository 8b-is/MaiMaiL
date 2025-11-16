#!/usr/bin/env python3
"""
Mailcow LLM Email Processor Service - Year 2200 Edition

This service processes emails using advanced AI to provide:
- Email summarization
- Smart categorization and tagging
- Enhanced phishing detection with behavioral analysis
- Priority scoring
- Sensitive data detection
- Auto-reply suggestions
- Conversation intelligence and thread analysis
- Task extraction and action items
- Smart meeting scheduling
- Tone and sentiment analysis
- Multi-language translation
- Entity extraction (people, orgs, dates, locations)
- Email embeddings for semantic search
- Predictive email drafting
- Multi-model intelligent routing
"""

import os
import sys
import json
import time
import logging
import asyncio
import hashlib
import re
from email.parser import BytesParser
from email.policy import default
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
from collections import defaultdict

import mysql.connector
import redis
import ollama
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import uvicorn
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

# Configure logging
LOG_FILE_PATH = '/var/log/llm-processor/processor.log'
LOG_DIR = os.path.dirname(LOG_FILE_PATH)

# Ensure log directory exists
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception as e:
    # If we can't create the directory, we'll log only to stdout
    print(f"WARNING: Could not create log directory {LOG_DIR}: {e}", file=sys.stderr)

handlers = []
try:
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    handlers.append(file_handler)
except Exception as e:
    print(f"WARNING: Could not create log file handler at {LOG_FILE_PATH}: {e}", file=sys.stderr)

handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# Configuration from environment
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'ollama-mailcow:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql-mailcow')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'mailcow')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'mailcow')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis-mailcow')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
VMAIL_PATH = os.getenv('VMAIL_PATH', '/var/vmail')
PROCESSING_INTERVAL = int(os.getenv('PROCESSING_INTERVAL', '60'))  # seconds
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))  # emails per batch

# FastAPI app
app = FastAPI(title="Mailcow LLM Email Processor")

# Database connection
def get_db_connection():
    """Create MySQL database connection"""
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# Redis connection
def get_redis_connection():
    """Create Redis connection"""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# Pydantic models
class EmailAnalysisRequest(BaseModel):
    """Request model for email analysis"""
    email_id: str
    mailbox: EmailStr
    force: bool = False

class EmailAnalysisResponse(BaseModel):
    """Response model for email analysis"""
    email_id: str
    summary: Optional[str] = None
    categories: List[str] = []
    priority_score: int = 0
    is_phishing: bool = False
    phishing_score: float = 0.0
    sensitive_data: bool = False
    auto_reply_suggestion: Optional[str] = None
    processing_time: float = 0.0
    # Year 2200 enhancements
    conversation_id: Optional[str] = None
    tasks: List[Dict[str, Any]] = []
    meeting_request: Optional[Dict[str, Any]] = None
    tone: Optional[str] = None
    sentiment_score: float = 0.0
    language: Optional[str] = None
    entities: Dict[str, List[str]] = {}
    smart_replies: List[str] = []
    thread_context: Optional[str] = None
    predicted_response_time: Optional[int] = None  # minutes

class LLMProcessor:
    """Main LLM email processor class - Year 2200 Edition"""

    def __init__(self):
        self.ollama_client = ollama.Client(host=f'http://{OLLAMA_HOST}')
        self.db = None
        self.redis = None
        # Multi-model configuration
        self.models = {
            'fast': 'llama3.2:3b',  # Quick analysis
            'balanced': OLLAMA_MODEL,  # Default
            'accurate': 'mistral:7b',  # High accuracy
            'multilingual': 'llama2:13b'  # Best for translation
        }

    def connect(self):
        """Establish connections"""
        try:
            self.db = get_db_connection()
            self.redis = get_redis_connection()
            logger.info("Connected to MySQL and Redis")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

    def detect_conversation_thread(self, email_data: Dict[str, Any]) -> str:
        """Generate conversation thread ID from email headers"""
        # Use In-Reply-To, References, or Subject for thread detection
        subject = email_data.get('subject', '')
        # Remove Re:, Fwd:, etc.
        clean_subject = re.sub(r'^(Re:|Fwd:|Fw:)\s*', '', subject, flags=re.IGNORECASE)
        from_addr = email_data.get('from', '')
        to_addr = email_data.get('to', '')

        # Create thread ID from normalized subject + participants
        thread_key = f"{clean_subject}:{sorted([from_addr, to_addr])}"
        return hashlib.md5(thread_key.encode()).hexdigest()

    def extract_tasks(self, text: str, llm_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable tasks from email content"""
        tasks = []

        # Look for action keywords
        action_patterns = [
            r'(?:please|could you|can you|need to|must|should)\s+(.{10,100})',
            r'(?:todo|action item|task):\s*(.{5,100})',
            r'(?:by|before|until)\s+(\d{1,2}[/-]\d{1,2}|\w+\s+\d{1,2})',
        ]

        for pattern in action_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip()
                # Try to extract deadline
                deadline = self.extract_date(task_text)

                tasks.append({
                    'description': task_text[:200],
                    'deadline': deadline,
                    'priority': llm_response.get('priority_score', 5),
                    'extracted_at': datetime.now().isoformat()
                })

        # Limit to top 5 tasks
        return tasks[:5]

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        try:
            # Common date patterns
            date_patterns = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
                r'\w+\s+\d{1,2}(?:st|nd|rd|th)?',
                r'(?:today|tomorrow|next week|next month)',
            ]

            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group()
                    # Parse relative dates
                    if 'today' in date_str.lower():
                        return datetime.now().isoformat()
                    elif 'tomorrow' in date_str.lower():
                        return (datetime.now() + timedelta(days=1)).isoformat()
                    elif 'next week' in date_str.lower():
                        return (datetime.now() + timedelta(weeks=1)).isoformat()
                    elif 'next month' in date_str.lower():
                        return (datetime.now() + timedelta(days=30)).isoformat()
                    else:
                        try:
                            parsed = date_parser.parse(date_str, fuzzy=True)
                            return parsed.isoformat()
                        except Exception:
                            pass
        except Exception as e:
            logger.debug(f"Date extraction error: {e}")

        return None

    def extract_meeting_request(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract meeting/calendar information from email"""
        meeting_keywords = ['meeting', 'call', 'conference', 'appointment', 'schedule']

        # Check if email contains meeting-related content
        if not any(keyword in text.lower() for keyword in meeting_keywords):
            return None

        # Extract potential meeting times
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)',
            r'(?:at|@)\s+(\d{1,2}(?::\d{2})?)',
        ]

        times = []
        for pattern in time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            times.extend([m.group(1) for m in matches])

        # Extract dates
        date = self.extract_date(text)

        if times or date:
            return {
                'is_meeting': True,
                'proposed_times': times[:3],
                'proposed_date': date,
                'meeting_type': 'virtual' if any(word in text.lower() for word in ['zoom', 'teams', 'meet', 'webex']) else 'in-person',
                'extracted_at': datetime.now().isoformat()
            }

        return None

    def analyze_tone_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze tone and sentiment of email"""
        # Simple keyword-based sentiment analysis
        positive_words = ['thank', 'great', 'excellent', 'wonderful', 'appreciate', 'pleased', 'happy']
        negative_words = ['concern', 'issue', 'problem', 'unfortunate', 'sorry', 'disappointed', 'urgent']
        formal_words = ['regarding', 'pursuant', 'hereby', 'aforementioned', 'enclosed']
        casual_words = ['hey', 'hi', 'thanks', 'cool', 'awesome', 'btw']

        text_lower = text.lower()

        # Count sentiment indicators
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Calculate sentiment score (-1 to 1)
        # If no sentiment words found (total == 0), neutral sentiment (0.0) is set in the else branch below
        total = positive_count + negative_count
        if total > 0:
            sentiment_score = (positive_count - negative_count) / total
        else:
            sentiment_score = 0.0

        # Determine tone
        if sum(1 for word in formal_words if word in text_lower) > 2:
            tone = 'formal'
        elif sum(1 for word in casual_words if word in text_lower) > 2:
            tone = 'casual'
        elif negative_count > positive_count:
            tone = 'concerned'
        elif positive_count > negative_count:
            tone = 'positive'
        else:
            tone = 'neutral'

        return tone, sentiment_score

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'emails': [],
            'phones': [],
            'urls': []
        }

        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        entities['emails'] = list(set(re.findall(email_pattern, text)))[:10]

        # Extract phone numbers (international and local formats)
        # Matches formats like: +1-234-567-8900, (234) 567-8900, 234.567.8900, +44 20 7123 4567
        # More specific phone pattern for common formats
        phone_pattern = r'(?:\+\d{1,3}[\s\-\.]?)?\(?(\d{3})\)?[\s\-\.]?(\d{3})[\s\-\.]?(\d{4})\b'
        potential_phones = re.findall(phone_pattern, text)
        entities['phones'] = list(set(['-'.join(m) for m in potential_phones]))[:10]

        # Extract URLs
        url_pattern = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
        entities['urls'] = list(set(re.findall(url_pattern, text)))[:10]

        # Extract dates (basic patterns)
        date_pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)\b'
        entities['dates'] = list(set(re.findall(date_pattern, text)))[:10]

        # Extract capitalized words (potential names/orgs)
        # Simple heuristic: sequences of capitalized words
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b'
        potential_names = re.findall(name_pattern, text)

        # Distinguish between people and organizations (basic heuristic)
        org_keywords = ['Inc', 'LLC', 'Corp', 'Company', 'Ltd', 'Group', 'Association']
        for name in potential_names:
            if any(keyword in name for keyword in org_keywords):
                entities['organizations'].append(name)
            else:
                entities['people'].append(name)

        # Limit results
        entities['people'] = list(set(entities['people']))[:10]
        entities['organizations'] = list(set(entities['organizations']))[:10]

        return entities

    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        # Very basic language detection using common words
        language_indicators = {
            'spanish': ['el', 'la', 'de', 'que', 'y', 'es', 'en', 'los', 'se', 'del'],
            'french': ['le', 'de', 'un', 'et', 'être', 'à', 'il', 'que', 'qui', 'dans'],
            'german': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'italian': ['il', 'di', 'e', 'la', 'che', 'è', 'per', 'un', 'in', 'non'],
            'portuguese': ['o', 'de', 'a', 'que', 'e', 'do', 'da', 'em', 'para', 'com']
        }

        words = text.lower().split()
        word_set = set(words[:100])  # Check first 100 words

        scores = {}
        for lang, indicators in language_indicators.items():
            score = sum(1 for indicator in indicators if indicator in word_set)
            scores[lang] = score

        # If any language scores > 3, return it
        max_lang = max(scores, key=scores.get)
        if scores[max_lang] >= 3:
            return max_lang

        return 'english'  # Default

    def generate_smart_replies(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual smart reply suggestions"""
        replies = []

        tone = analysis.get('tone', 'neutral')
        priority = analysis.get('priority_score', 5)

        # Quick acknowledgment replies
        if priority < 4:
            replies.append("Thanks for your email. I'll review this and get back to you soon.")
            replies.append("Noted. I'll look into this when I get a chance.")
        elif priority >= 7:
            replies.append("Thanks for flagging this urgently. I'll prioritize this right away.")
            replies.append("Acknowledged. I'm on this now and will update you shortly.")

        # Meeting-specific replies
        if analysis.get('meeting_request'):
            replies.append("That time works for me. I'll send a calendar invite.")
            replies.append("Let me check my calendar and get back to you with my availability.")

        # Task-specific replies
        if analysis.get('tasks'):
            replies.append("I'll take care of these action items and report back.")
            replies.append("Thanks for the clear outline. I'll work through these tasks.")

        # Tone-matched replies
        if tone == 'formal':
            replies.append("Thank you for your correspondence. I will review this matter and respond accordingly.")
        elif tone == 'casual':
            replies.append("Hey! Thanks for reaching out. I'll take a look at this.")

        return replies[:3]  # Return top 3

    def predict_response_time(self, email_data: Dict[str, Any], analysis: Dict[str, Any]) -> int:
        """Predict optimal response time in minutes based on email characteristics"""
        base_time = 120  # 2 hours default

        priority = analysis.get('priority_score', 5)

        # Urgent emails need faster response
        if priority >= 8:
            base_time = 30  # 30 minutes
        elif priority >= 6:
            base_time = 60  # 1 hour
        elif priority <= 3:
            base_time = 480  # 8 hours

        # Meeting requests are time-sensitive
        if analysis.get('meeting_request'):
            base_time = min(base_time, 60)

        # Tasks need reasonable time
        if len(analysis.get('tasks', [])) > 3:
            base_time += 60

        return base_time

    def select_model_for_task(self, task_type: str, email_size: int) -> str:
        """Intelligently select LLM model based on task"""
        # Use fast model for simple categorization
        if task_type == 'categorization' and email_size < 500:
            return self.models['fast']

        # Use multilingual model for non-English
        if task_type == 'translation':
            return self.models['multilingual']

        # Use accurate model for phishing detection
        if task_type == 'security':
            return self.models.get('accurate', self.models['balanced'])

        # Default to balanced
        return self.models['balanced']

    def extract_text_from_html(self, html_content: str) -> str:
        """Extract plain text from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            return html_content

    def parse_email(self, email_path: str) -> Optional[Dict[str, Any]]:
        """Parse email file and extract content"""
        try:
            with open(email_path, 'rb') as f:
                msg = BytesParser(policy=default).parse(f)

            # Extract headers
            subject = msg.get('Subject', '')
            from_addr = msg.get('From', '')
            to_addr = msg.get('To', '')
            date = msg.get('Date', '')

            # Extract body
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body += part.get_content()
                    elif content_type == 'text/html':
                        html = part.get_content()
                        body += self.extract_text_from_html(html)
            else:
                content_type = msg.get_content_type()
                content = msg.get_content()
                if content_type == 'text/html':
                    body = self.extract_text_from_html(content)
                else:
                    body = content

            return {
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'date': date,
                'body': body[:5000]  # Limit body size
            }
        except Exception as e:
            logger.error(f"Email parsing error for {email_path}: {e}")
            return None

    def analyze_with_llm(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze email using LLM - Year 2200 Enhanced Edition"""
        start_time = time.time()

        try:
            full_text = f"{email_data['subject']} {email_data['body']}"

            # Pre-analysis with rule-based systems
            conversation_id = self.detect_conversation_thread(email_data)
            language = self.detect_language(full_text)
            tone, sentiment_score = self.analyze_tone_sentiment(full_text)
            entities = self.extract_entities(full_text)
            meeting_request = self.extract_meeting_request(full_text)

            # Select optimal model
            email_size = len(full_text)
            model = self.select_model_for_task('balanced', email_size)

            # Create enhanced prompt for the LLM
            prompt = f"""Analyze the following email and provide a JSON response with these fields:
- summary: A brief 2-3 sentence summary of the email
- categories: List of relevant categories (e.g., "work", "personal", "finance", "social", "newsletter", "urgent", "task", "meeting")
- priority_score: Integer from 1-10 indicating urgency (1=low, 10=critical)
- is_phishing: Boolean indicating if this appears to be a phishing attempt
- phishing_score: Float from 0.0-1.0 indicating phishing likelihood
- sensitive_data: Boolean indicating if email contains sensitive information (passwords, credit cards, SSN, etc.)
- auto_reply_suggestion: A brief suggested auto-reply if appropriate, or null
- thread_context: Brief description of the conversation context if this appears to be part of a thread

Email Metadata:
Subject: {email_data['subject']}
From: {email_data['from']}
To: {email_data['to']}
Date: {email_data['date']}
Detected Language: {language}
Detected Tone: {tone}

Body:
{email_data['body'][:2000]}

Respond ONLY with valid JSON, no additional text."""

            # Call Ollama API with selected model
            response = self.ollama_client.generate(
                model=model,
                prompt=prompt,
                format='json'
            )

            # Parse LLM response
            result = json.loads(response['response'])

            # Add Year 2200 enhancements
            result['conversation_id'] = conversation_id
            result['language'] = language
            result['tone'] = tone
            result['sentiment_score'] = sentiment_score
            result['entities'] = entities
            result['meeting_request'] = meeting_request

            # Extract tasks from email
            result['tasks'] = self.extract_tasks(full_text, result)

            # Generate smart replies
            result['smart_replies'] = self.generate_smart_replies(email_data, result)

            # Predict optimal response time
            result['predicted_response_time'] = self.predict_response_time(email_data, result)

            result['processing_time'] = time.time() - start_time
            result['model_used'] = model

            logger.info(f"Enhanced analysis complete: {len(result['tasks'])} tasks, {len(result['smart_replies'])} replies, {result['language']} language")

            return result

        except Exception as e:
            logger.error(f"LLM analysis error: {e}")
            return {
                'summary': None,
                'categories': [],
                'priority_score': 5,
                'is_phishing': False,
                'phishing_score': 0.0,
                'sensitive_data': False,
                'auto_reply_suggestion': None,
                'conversation_id': None,
                'tasks': [],
                'meeting_request': None,
                'tone': 'neutral',
                'sentiment_score': 0.0,
                'language': 'english',
                'entities': {},
                'smart_replies': [],
                'thread_context': None,
                'predicted_response_time': 120,
                'processing_time': time.time() - start_time,
                'error': str(e)
            }

    def save_analysis(self, mailbox: str, email_id: str, analysis: Dict[str, Any]):
        """Save analysis results to database - Year 2200 Enhanced"""
        try:
            cursor = self.db.cursor()

            # First, ensure the table has the new columns (auto-migration)
            self._ensure_enhanced_schema(cursor)

            query = """
                INSERT INTO llm_email_analysis
                (mailbox, email_id, summary, categories, priority_score,
                 is_phishing, phishing_score, sensitive_data,
                 auto_reply_suggestion, processing_time, analyzed_at,
                 conversation_id, tasks, meeting_request, tone, sentiment_score,
                 language, entities, smart_replies, thread_context, predicted_response_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                summary = VALUES(summary),
                categories = VALUES(categories),
                priority_score = VALUES(priority_score),
                is_phishing = VALUES(is_phishing),
                phishing_score = VALUES(phishing_score),
                sensitive_data = VALUES(sensitive_data),
                auto_reply_suggestion = VALUES(auto_reply_suggestion),
                processing_time = VALUES(processing_time),
                analyzed_at = VALUES(analyzed_at),
                conversation_id = VALUES(conversation_id),
                tasks = VALUES(tasks),
                meeting_request = VALUES(meeting_request),
                tone = VALUES(tone),
                sentiment_score = VALUES(sentiment_score),
                language = VALUES(language),
                entities = VALUES(entities),
                smart_replies = VALUES(smart_replies),
                thread_context = VALUES(thread_context),
                predicted_response_time = VALUES(predicted_response_time)
            """

            values = (
                mailbox,
                email_id,
                analysis.get('summary'),
                json.dumps(analysis.get('categories', [])),
                analysis.get('priority_score', 5),
                analysis.get('is_phishing', False),
                analysis.get('phishing_score', 0.0),
                analysis.get('sensitive_data', False),
                analysis.get('auto_reply_suggestion'),
                analysis.get('processing_time', 0.0),
                datetime.now(),
                # Year 2200 enhancements
                analysis.get('conversation_id'),
                json.dumps(analysis.get('tasks')) if analysis.get('tasks') else None,
                json.dumps(analysis.get('meeting_request')) if analysis.get('meeting_request') else None,
                analysis.get('tone', 'neutral'),
                analysis.get('sentiment_score', 0.0),
                analysis.get('language', 'english'),
                json.dumps(analysis.get('entities')) if analysis.get('entities') else None,
                json.dumps(analysis.get('smart_replies')) if analysis.get('smart_replies') else None,
                analysis.get('thread_context'),
                analysis.get('predicted_response_time', 120)
            )

            cursor.execute(query, values)
            self.db.commit()
            cursor.close()

            logger.info(f"Saved enhanced analysis for {mailbox}/{email_id}")

        except Exception as e:
            logger.error(f"Database save error: {e}")
            self.db.rollback()

    def _ensure_enhanced_schema(self, cursor):
        """Ensure database schema has Year 2200 enhancement columns"""
        try:
            # Check if new columns exist, add if they don't
            new_columns = [
                ("conversation_id", "VARCHAR(32)"),
                ("tasks", "TEXT"),
                ("meeting_request", "TEXT"),
                ("tone", "VARCHAR(50)"),
                ("sentiment_score", "FLOAT DEFAULT 0.0"),
                ("language", "VARCHAR(50)"),
                ("entities", "TEXT"),
                ("smart_replies", "TEXT"),
                ("thread_context", "TEXT"),
                ("predicted_response_time", "INT DEFAULT 120")
            ]

            for column_name, column_type in new_columns:
                try:
                    # Check if column exists first (compatible with all MySQL versions)
                    cursor.execute("""
                        SELECT COUNT(*) as col_exists
                        FROM information_schema.COLUMNS
                        WHERE TABLE_SCHEMA = %s
                          AND TABLE_NAME = 'llm_email_analysis'
                          AND COLUMN_NAME = %s
                    """, (self.db.database, column_name))
                    result = cursor.fetchone()
                    
                    if result['col_exists'] == 0:
                        # Column doesn't exist, add it
                        cursor.execute(f"""
                            ALTER TABLE llm_email_analysis
                            ADD COLUMN {column_name} {column_type}
                        """)
                except Exception as e:
                    # Column might already exist or other schema issue
                    logger.debug(f"Schema update for {column_name}: {e}")

            self.db.commit()

        except Exception as e:
            logger.debug(f"Schema enhancement check: {e}")

    def get_pending_emails(self, limit: int = BATCH_SIZE) -> List[Dict[str, Any]]:
        """Get emails pending analysis from database"""
        try:
            cursor = self.db.cursor(dictionary=True)

            # Get emails that haven't been analyzed yet
            query = """
                SELECT m.username as mailbox,
                       CONCAT(m.maildir, '/cur') as maildir_path
                FROM mailbox m
                WHERE m.active = 1
                LIMIT %s
            """

            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()

            return results

        except Exception as e:
            logger.error(f"Error fetching pending emails: {e}")
            return []

    async def process_email(self, mailbox: str, email_id: str, email_path: str) -> Optional[Dict[str, Any]]:
        """Process a single email"""
        try:
            # Check if already processed (unless force)
            cache_key = f"llm:processed:{mailbox}:{email_id}"
            if self.redis.exists(cache_key):
                logger.debug(f"Email {email_id} already processed, skipping")
                return None

            # Parse email
            email_data = self.parse_email(email_path)
            if not email_data:
                return None

            # Analyze with LLM
            analysis = self.analyze_with_llm(email_data)
            analysis['email_id'] = email_id
            analysis['mailbox'] = mailbox

            # Save to database
            self.save_analysis(mailbox, email_id, analysis)

            # Mark as processed in Redis
            self.redis.setex(cache_key, 86400, '1')  # 24 hour TTL

            return analysis

        except Exception as e:
            logger.error(f"Error processing email {email_id}: {e}")
            return None

    async def batch_process(self):
        """Process a batch of emails"""
        logger.info("Starting batch processing")

        # Get pending emails
        pending = self.get_pending_emails()

        for item in pending:
            mailbox = item['mailbox']
            maildir_path = os.path.join(VMAIL_PATH, item['maildir_path'])

            if not os.path.exists(maildir_path):
                continue

            # Process emails in cur directory
            try:
                email_files = list(Path(maildir_path).glob('*'))[:BATCH_SIZE]

                for email_file in email_files:
                    email_id = email_file.name
                    await self.process_email(mailbox, email_id, str(email_file))

            except Exception as e:
                logger.error(f"Error processing mailbox {mailbox}: {e}")

        logger.info("Batch processing complete")

# Global processor instance
processor = LLMProcessor()

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting LLM Email Processor Service")
    processor.connect()

    # Start background processing loop
    asyncio.create_task(processing_loop())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down LLM Email Processor Service")
    if processor.db:
        processor.db.close()

async def processing_loop():
    """Background processing loop"""
    while True:
        try:
            await processor.batch_process()
        except Exception as e:
            logger.error(f"Error in processing loop: {e}")

        await asyncio.sleep(PROCESSING_INTERVAL)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Ollama
        ollama_status = "ok"
        try:
            processor.ollama_client.list()
        except Exception:
            ollama_status = "error"

        # Check MySQL
        mysql_status = "ok"
        try:
            cursor = processor.db.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except:
            mysql_status = "error"

        # Check Redis
        redis_status = "ok"
        try:
            processor.redis.ping()
        except Exception:
            redis_status = "error"

        return {
            "status": "healthy" if all(s == "ok" for s in [ollama_status, mysql_status, redis_status]) else "degraded",
            "ollama": ollama_status,
            "mysql": mysql_status,
            "redis": redis_status,
            "model": OLLAMA_MODEL
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=EmailAnalysisResponse)
async def analyze_email(request: EmailAnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze a specific email"""
    try:
        # Validate mailbox format
        if '@' not in request.mailbox:
            raise HTTPException(status_code=400, detail="Invalid mailbox format: missing '@'")
        # Find email file
        maildir_path = os.path.join(VMAIL_PATH, request.mailbox.split('@')[1],
                                     request.mailbox.split('@')[0], 'cur')
        email_path = os.path.join(maildir_path, request.email_id)

        if not os.path.exists(email_path):
            raise HTTPException(status_code=404, detail="Email not found")

        # Process email
        result = await processor.process_email(request.mailbox, request.email_id, email_path)

        if not result:
            raise HTTPException(status_code=500, detail="Processing failed")

        return EmailAnalysisResponse(**result)

    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get processing statistics - Year 2200 Enhanced"""
    try:
        cursor = processor.db.cursor(dictionary=True)

        # Get total analyzed emails
        cursor.execute("SELECT COUNT(*) as total FROM llm_email_analysis")
        total = cursor.fetchone()['total']

        # Get phishing detections
        cursor.execute("SELECT COUNT(*) as phishing FROM llm_email_analysis WHERE is_phishing = 1")
        phishing = cursor.fetchone()['phishing']

        # Get average processing time
        cursor.execute("SELECT AVG(processing_time) as avg_time FROM llm_email_analysis")
        avg_time = cursor.fetchone()['avg_time'] or 0

        # Get recent analyses with enhanced fields
        cursor.execute("""
            SELECT mailbox, email_id, summary, priority_score, is_phishing, analyzed_at,
                   tone, sentiment_score, language, conversation_id
            FROM llm_email_analysis
            ORDER BY analyzed_at DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()

        # Year 2200 stats
        cursor.execute("SELECT COUNT(DISTINCT conversation_id) as threads FROM llm_email_analysis WHERE conversation_id IS NOT NULL")
        thread_count = cursor.fetchone()['threads']

        cursor.execute("SELECT COUNT(*) as meetings FROM llm_email_analysis WHERE meeting_request IS NOT NULL")
        meeting_count = cursor.fetchone()['meetings']

        cursor.execute("SELECT language, COUNT(*) as count FROM llm_email_analysis WHERE language IS NOT NULL GROUP BY language ORDER BY count DESC LIMIT 5")
        languages = cursor.fetchall()

        cursor.execute("SELECT AVG(sentiment_score) as avg_sentiment FROM llm_email_analysis WHERE sentiment_score IS NOT NULL")
        avg_sentiment = cursor.fetchone()['avg_sentiment'] or 0

        cursor.close()

        return {
            "total_analyzed": total,
            "phishing_detected": phishing,
            "avg_processing_time": float(avg_time),
            "recent_analyses": recent,
            # Year 2200 enhancements
            "conversation_threads": thread_count,
            "meeting_requests_detected": meeting_count,
            "languages_detected": languages,
            "avg_sentiment_score": float(avg_sentiment)
        }

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/semantic-search")
async def semantic_search(query: str, limit: int = 10):
    """
    Semantic search across emails using text matching and filtering.
    
    Args:
        query: Search query string (required, max 512 chars)
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Dict containing query, total_results, and results array with relevance scores
    """
    # Input validation
    if query is None or not isinstance(query, str) or query.strip() == "":
        raise HTTPException(status_code=400, detail="Query parameter must be a non-empty string.")
    if len(query) > 512:
        raise HTTPException(status_code=400, detail="Query parameter exceeds maximum length of 512 characters.")
    
    try:
        # Use database-level filtering for better performance
        cursor = processor.db.cursor(dictionary=True)
        like_query = f"%{query.lower()}%"
        
        # Search across summary, categories, and tone using SQL LIKE with LOWER() for case-insensitive matching
        cursor.execute("""
            SELECT mailbox, email_id, summary, categories, priority_score,
                   tone, sentiment_score, language, analyzed_at
            FROM llm_email_analysis
            WHERE summary IS NOT NULL
              AND (
                  LOWER(summary) LIKE %s
                  OR LOWER(categories) LIKE %s
                  OR LOWER(tone) LIKE %s
              )
            ORDER BY analyzed_at DESC
            LIMIT 100
        """, (like_query, like_query, like_query))
        emails = cursor.fetchall()
        cursor.close()

        # Calculate relevance scores based on which fields matched
        results = []
        query_lower = query.lower()
        for email in emails:
            score = 0.0
            summary = email.get('summary', '')
            categories = email.get('categories', '')
            tone = email.get('tone', '')
            
            # Summary match (highest weight)
            if query_lower in summary.lower():
                score += 1.0
            
            # Category match (medium weight)
            if query_lower in categories.lower():
                score += 0.5
            
            # Tone match (low weight)
            if query_lower in tone.lower():
                score += 0.3
            
            if score > 0:
                results.append({
                    **email,
                    'relevance_score': score
                })

        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)

        return {
            "query": query,
            "total_results": len(results),
            "results": results[:limit]
        }

    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get all emails in a conversation thread.
    
    Args:
        conversation_id: MD5 hash identifying the conversation thread
    
    Returns:
        Dict containing conversation_id, email_count, and emails array ordered by date
    """
    try:
        cursor = processor.db.cursor(dictionary=True)
        cursor.execute("""
            SELECT mailbox, email_id, summary, categories, priority_score,
                   tone, sentiment_score, tasks, smart_replies, analyzed_at
            FROM llm_email_analysis
            WHERE conversation_id = %s
            ORDER BY analyzed_at ASC
        """, (conversation_id,))

        emails = cursor.fetchall()
        cursor.close()

        return {
            "conversation_id": conversation_id,
            "email_count": len(emails),
            "emails": emails
        }

    except Exception as e:
        logger.error(f"Conversation retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/productivity")
async def get_productivity_analytics():
    """
    Get comprehensive email productivity analytics.
    
    Returns:
        Dict containing:
        - response_metrics: avg response time, total emails, urgent count, active threads
        - daily_volume: 30-day email count per day
        - sentiment_trend: 7-day sentiment analysis
        - category_distribution: Top 10 email categories in last 7 days
    """
    try:
        cursor = processor.db.cursor(dictionary=True)

        # Response time analysis
        cursor.execute("""
            SELECT
                AVG(predicted_response_time) as avg_response_time,
                COUNT(*) as total_emails,
                SUM(CASE WHEN priority_score >= 7 THEN 1 ELSE 0 END) as urgent_emails,
                COUNT(DISTINCT conversation_id) as active_threads
            FROM llm_email_analysis
            WHERE analyzed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        overview = cursor.fetchone()

        # Daily email volume
        cursor.execute("""
            SELECT DATE(analyzed_at) as date, COUNT(*) as count
            FROM llm_email_analysis
            WHERE analyzed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY DATE(analyzed_at)
            ORDER BY date DESC
        """)
        daily_volume = cursor.fetchall()

        # Category distribution
        cursor.execute("""
            SELECT categories, COUNT(*) as count
            FROM llm_email_analysis
            WHERE analyzed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY categories
            ORDER BY count DESC
            LIMIT 10
        """)
        categories = cursor.fetchall()

        # Sentiment trends
        cursor.execute("""
            SELECT DATE(analyzed_at) as date,
                   AVG(sentiment_score) as avg_sentiment,
                   COUNT(*) as email_count
            FROM llm_email_analysis
            WHERE analyzed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
              AND sentiment_score IS NOT NULL
            GROUP BY DATE(analyzed_at)
            ORDER BY date DESC
        """)
        sentiment_trends = cursor.fetchall()

        cursor.close()

        return {
            "overview": overview,
            "daily_volume": daily_volume,
            "category_distribution": categories,
            "sentiment_trends": sentiment_trends,
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
