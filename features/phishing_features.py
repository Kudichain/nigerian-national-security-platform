"""Email/phishing feature extraction."""

import re
import tldextract
import pandas as pd
from typing import Dict, Any, List
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhishingFeatureExtractor:
    """Extract features from emails for phishing detection."""
    
    def extract_email_features(self, email: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract all features from an email message.
        
        Args:
            email: Email message dictionary
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Header features
        features.update(self._extract_header_features(email))
        
        # URL features
        features.update(self._extract_url_features(email.get('urls', [])))
        
        # Text features
        features.update(self._extract_text_features(
            email.get('subject', ''),
            email.get('body_text', '')
        ))
        
        # Attachment features
        features.update(self._extract_attachment_features(email.get('attachments', [])))
        
        # Authentication features
        features.update(self._extract_auth_features(email))
        
        return features
    
    def _extract_header_features(self, email: Dict[str, Any]) -> Dict[str, float]:
        """Extract features from email headers."""
        from_addr = email.get('from_addr', '')
        
        features = {
            # Sender domain features
            'sender_domain_length': float(len(self._extract_domain(from_addr))),
            'sender_has_subdomain': 1.0 if from_addr.count('.') > 1 else 0.0,
            'sender_uses_numbers': 1.0 if any(c.isdigit() for c in from_addr) else 0.0,
            
            # Recipient count
            'recipient_count': float(len(email.get('to_addrs', []))),
            
            # Subject features
            'subject_length': float(len(email.get('subject', ''))),
            'subject_has_urgent': 1.0 if self._contains_urgent_keywords(
                email.get('subject', '')
            ) else 0.0,
        }
        
        return features
    
    def _extract_url_features(self, urls: List[str]) -> Dict[str, float]:
        """Extract features from URLs in email."""
        if not urls:
            return {
                'url_count': 0.0,
                'suspicious_tld_count': 0.0,
                'ip_address_url_count': 0.0,
                'url_shortener_count': 0.0,
                'avg_url_length': 0.0,
            }
        
        suspicious_tlds = {'.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq'}
        url_shorteners = {'bit.ly', 'tinyurl.com', 'goo.gl', 't.co'}
        
        features = {
            'url_count': float(len(urls)),
            'suspicious_tld_count': 0.0,
            'ip_address_url_count': 0.0,
            'url_shortener_count': 0.0,
            'avg_url_length': float(sum(len(url) for url in urls) / len(urls)),
            'max_url_length': float(max(len(url) for url in urls)),
        }
        
        for url in urls:
            # Check for IP address
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                features['ip_address_url_count'] += 1.0
            
            # Extract domain
            try:
                extracted = tldextract.extract(url)
                domain = f"{extracted.domain}.{extracted.suffix}"
                
                # Check suspicious TLD
                if any(tld in url.lower() for tld in suspicious_tlds):
                    features['suspicious_tld_count'] += 1.0
                
                # Check URL shorteners
                if any(shortener in domain for shortener in url_shorteners):
                    features['url_shortener_count'] += 1.0
            except Exception:
                pass
        
        return features
    
    def _extract_text_features(self, subject: str, body: str) -> Dict[str, float]:
        """Extract features from email text content."""
        combined_text = f"{subject} {body}".lower()
        
        # Phishing keywords
        urgent_keywords = ['urgent', 'immediate', 'action required', 'verify', 'suspended']
        financial_keywords = ['bank', 'account', 'payment', 'credit card', 'paypal']
        threat_keywords = ['suspended', 'locked', 'unauthorized', 'compromised']
        
        features = {
            'body_length': float(len(body)),
            'subject_body_ratio': self._safe_divide(len(subject), len(body)),
            
            # Keyword counts
            'urgent_keyword_count': float(sum(
                combined_text.count(kw) for kw in urgent_keywords
            )),
            'financial_keyword_count': float(sum(
                combined_text.count(kw) for kw in financial_keywords
            )),
            'threat_keyword_count': float(sum(
                combined_text.count(kw) for kw in threat_keywords
            )),
            
            # Character features
            'exclamation_count': float(combined_text.count('!')),
            'question_count': float(combined_text.count('?')),
            'uppercase_ratio': self._compute_uppercase_ratio(combined_text),
        }
        
        return features
    
    def _extract_attachment_features(self, attachments: List[str]) -> Dict[str, float]:
        """Extract features from email attachments."""
        return {
            'attachment_count': float(len(attachments)),
            'has_attachments': 1.0 if len(attachments) > 0 else 0.0,
        }
    
    def _extract_auth_features(self, email: Dict[str, Any]) -> Dict[str, float]:
        """Extract authentication-related features (SPF, DKIM, DMARC)."""
        return {
            'spf_pass': 1.0 if email.get('spf_result') == 'pass' else 0.0,
            'spf_fail': 1.0 if email.get('spf_result') == 'fail' else 0.0,
            'dkim_pass': 1.0 if email.get('dkim_result') == 'pass' else 0.0,
            'dkim_fail': 1.0 if email.get('dkim_result') == 'fail' else 0.0,
            'dmarc_pass': 1.0 if email.get('dmarc_result') == 'pass' else 0.0,
            'dmarc_fail': 1.0 if email.get('dmarc_result') == 'fail' else 0.0,
        }
    
    @staticmethod
    def _extract_domain(email_addr: str) -> str:
        """Extract domain from email address."""
        if '@' in email_addr:
            return email_addr.split('@')[1]
        return email_addr
    
    @staticmethod
    def _contains_urgent_keywords(text: str) -> bool:
        """Check if text contains urgent/phishing keywords."""
        urgent_keywords = [
            'urgent', 'immediate', 'action required', 'verify now',
            'suspended', 'confirm', 'click here'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in urgent_keywords)
    
    @staticmethod
    def _compute_uppercase_ratio(text: str) -> float:
        """Compute ratio of uppercase letters."""
        if not text:
            return 0.0
        uppercase_count = sum(1 for c in text if c.isupper())
        return uppercase_count / len(text)
    
    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> float:
        """Safe division."""
        return numerator / denominator if denominator != 0 else 0.0


if __name__ == "__main__":
    extractor = PhishingFeatureExtractor()
    
    email = {
        'from_addr': 'admin@paypa1.com',
        'to_addrs': ['user@company.com'],
        'subject': 'URGENT: Verify your account NOW!',
        'body_text': 'Click here immediately or your account will be suspended.',
        'urls': ['http://paypa1-verify.xyz/login'],
        'spf_result': 'fail',
        'dkim_result': 'none',
        'dmarc_result': 'fail',
    }
    
    features = extractor.extract_email_features(email)
    print("Phishing features:", features)
