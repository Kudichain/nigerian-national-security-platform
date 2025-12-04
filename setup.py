"""Setup configuration for Security AI Platform."""

from setuptools import setup, find_packages

setup(
    name="sec-ai-platform",
    version="0.1.0",
    description="Production-grade security AI platform for threat detection",
    author="Security AI Team",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "sec-ai-train=models.cli:train",
            "sec-ai-serve=services.cli:serve",
        ]
    },
)
