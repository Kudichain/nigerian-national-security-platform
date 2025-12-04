"""Collectors package initialization."""

from collectors.netflow_agent import NetFlowCollector
from collectors.log_agent import LogCollector
from collectors.email_agent import EmailCollector
from collectors.auth_agent import AuthCollector
from collectors.malware_agent import MalwareCollector

__all__ = [
    "NetFlowCollector",
    "LogCollector",
    "EmailCollector",
    "AuthCollector",
    "MalwareCollector",
]
