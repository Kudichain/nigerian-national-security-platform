"""Email parser for extracting features from emails."""

import re
import email
import logging
from typing import List, Optional, Dict, Any
from email.message import Message
from email.utils import parseaddr
from bs4 import BeautifulSoup
from schemas.data_schemas import EmailMessage
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailParser:
    """Parse and extract features from email messages."""
    
    @staticmethod
    def parse_raw_email(raw_email: str) -> Optional[EmailMessage]:
        """
        Parse raw RFC 822 email message.
        
        Args:
            raw_email: Raw email string
            
        Returns:
            Normalized EmailMessage or None if invalid
        """
        try:
            msg = email.message_from_string(raw_email)
            
            # Extract addresses
            from_addr = parseaddr(msg.get('From', ''))[1]
            to_addrs = [parseaddr(addr)[1] for addr in msg.get_all('To', [])]
            
            # Extract body
            body_text, body_html = EmailParser._extract_body(msg)
            
            # Extract URLs
            urls = EmailParser._extract_urls(body_text or '', body_html or '')
            
            # Extract attachment hashes
            attachments = EmailParser._extract_attachment_hashes(msg)
            
            # Extract authentication results
            spf = EmailParser._extract_auth_result(msg, 'spf')
            dkim = EmailParser._extract_auth_result(msg, 'dkim')
            dmarc = EmailParser._extract_auth_result(msg, 'dmarc')
            
            return EmailMessage(
                msg_id=msg.get('Message-ID', f"<{hash(raw_email)}>"),
                ts=EmailParser._parse_date(msg.get('Date')),
                **{"from": from_addr},
                to=to_addrs,
                subject=msg.get('Subject', ''),
                body_text=body_text,
                body_html=body_html,
                attachments=attachments,
                spf_result=spf,
                dkim_result=dkim,
                dmarc_result=dmarc,
                urls=urls,
                label=None
            )
        except Exception as e:
            logger.error(f"Failed to parse email: {e}")
            return None
    
    @staticmethod
    def _extract_body(msg: Message) -> tuple[Optional[str], Optional[str]]:
        """Extract plain text and HTML body."""
        body_text = None
        body_html = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' and not body_text:
                    body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif content_type == 'text/html' and not body_html:
                    body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            if content_type == 'text/plain':
                body_text = payload
            elif content_type == 'text/html':
                body_html = payload
        
        return body_text, body_html
    
    @staticmethod
    def _extract_urls(text: str, html: str) -> List[str]:
        """Extract all URLs from text and HTML."""
        urls = set()
        
        # Extract from plain text
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(url_pattern, text))
        
        # Extract from HTML
        if html:
            soup = BeautifulSoup(html, 'lxml')
            for link in soup.find_all('a', href=True):
                urls.add(link['href'])
        
        return list(urls)
    
    @staticmethod
    def _extract_attachment_hashes(msg: Message) -> List[str]:
        """Extract SHA256 hashes of attachments."""
        import hashlib
        
        hashes = []
        for part in msg.walk():
            if part.get_content_disposition() == 'attachment':
                payload = part.get_payload(decode=True)
                if payload:
                    # Ensure payload is bytes
                    payload_bytes = payload if isinstance(payload, bytes) else str(payload).encode('utf-8')
                    hash_obj = hashlib.sha256(payload_bytes)
                    hashes.append(hash_obj.hexdigest())
        
        return hashes
    
    @staticmethod
    def _extract_auth_result(msg: Message, auth_type: str) -> Optional[str]:
        """Extract SPF/DKIM/DMARC results from headers."""
        auth_results = msg.get('Authentication-Results', '')
        
        pattern = rf'{auth_type}=(\w+)'
        match = re.search(pattern, auth_results, re.IGNORECASE)
        
        return match.group(1).lower() if match else None
    
    @staticmethod
    def _parse_date(date_str: Optional[str]) -> datetime:
        """Parse email date header."""
        if not date_str:
            return datetime.utcnow()
        
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.utcnow()


if __name__ == "__main__":
    # Example usage
    parser = EmailParser()
    
    raw = """From: attacker@evil.com
To: victim@company.com
Subject: Urgent Account Verification
Date: Wed, 27 Nov 2025 10:00:00 +0000
Message-ID: <12345@evil.com>

Click here to verify: http://phishing-site.xyz/login
"""
    
    email_msg = parser.parse_raw_email(raw)
    print(f"Parsed email: {email_msg}")
