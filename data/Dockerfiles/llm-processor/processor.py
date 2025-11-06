#!/usr/bin/env python3
"""
Mailcow LLM Email Processor Service

This service processes emails using a local LLM to provide:
- Email summarization
- Smart categorization and tagging
- Enhanced phishing detection
- Priority scoring
- Sensitive data detection
- Auto-reply suggestions
"""

import os
import sys
import json
import time
import logging
import asyncio
import email
from email.parser import BytesParser
from email.policy import default
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

import mysql.connector
import redis
import ollama
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
import uvicorn
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/llm-processor/processor.log'),
        logging.StreamHandler(sys.stdout)
    ]
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

class LLMProcessor:
    """Main LLM email processor class"""

    def __init__(self):
        self.ollama_client = ollama.Client(host=f'http://{OLLAMA_HOST}')
        self.db = None
        self.redis = None

    def connect(self):
        """Establish connections"""
        try:
            self.db = get_db_connection()
            self.redis = get_redis_connection()
            logger.info("Connected to MySQL and Redis")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise

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
        """Analyze email using LLM"""
        start_time = time.time()

        try:
            # Create prompt for the LLM
            prompt = f"""Analyze the following email and provide a JSON response with these fields:
- summary: A brief 2-3 sentence summary of the email
- categories: List of relevant categories (e.g., "work", "personal", "finance", "social", "newsletter", "urgent")
- priority_score: Integer from 1-10 indicating urgency (1=low, 10=critical)
- is_phishing: Boolean indicating if this appears to be a phishing attempt
- phishing_score: Float from 0.0-1.0 indicating phishing likelihood
- sensitive_data: Boolean indicating if email contains sensitive information (passwords, credit cards, SSN, etc.)
- auto_reply_suggestion: A brief suggested auto-reply if appropriate, or null

Email:
Subject: {email_data['subject']}
From: {email_data['from']}
To: {email_data['to']}
Date: {email_data['date']}

Body:
{email_data['body'][:2000]}

Respond ONLY with valid JSON, no additional text."""

            # Call Ollama API
            response = self.ollama_client.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                format='json'
            )

            # Parse response
            result = json.loads(response['response'])
            result['processing_time'] = time.time() - start_time

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
                'processing_time': time.time() - start_time,
                'error': str(e)
            }

    def save_analysis(self, mailbox: str, email_id: str, analysis: Dict[str, Any]):
        """Save analysis results to database"""
        try:
            cursor = self.db.cursor()

            query = """
                INSERT INTO llm_email_analysis
                (mailbox, email_id, summary, categories, priority_score,
                 is_phishing, phishing_score, sensitive_data,
                 auto_reply_suggestion, processing_time, analyzed_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                summary = VALUES(summary),
                categories = VALUES(categories),
                priority_score = VALUES(priority_score),
                is_phishing = VALUES(is_phishing),
                phishing_score = VALUES(phishing_score),
                sensitive_data = VALUES(sensitive_data),
                auto_reply_suggestion = VALUES(auto_reply_suggestion),
                processing_time = VALUES(processing_time),
                analyzed_at = VALUES(analyzed_at)
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
                datetime.now()
            )

            cursor.execute(query, values)
            self.db.commit()
            cursor.close()

            logger.info(f"Saved analysis for {mailbox}/{email_id}")

        except Exception as e:
            logger.error(f"Database save error: {e}")
            self.db.rollback()

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
        except:
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
    """Get processing statistics"""
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

        # Get recent analyses
        cursor.execute("""
            SELECT mailbox, email_id, summary, priority_score, is_phishing, analyzed_at
            FROM llm_email_analysis
            ORDER BY analyzed_at DESC
            LIMIT 10
        """)
        recent = cursor.fetchall()

        cursor.close()

        return {
            "total_analyzed": total,
            "phishing_detected": phishing,
            "avg_processing_time": float(avg_time),
            "recent_analyses": recent
        }

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
