"""
Nigerian Language Support & Localization
Award-Winning Feature: Cultural & Linguistic Inclusivity

Provides multi-language support for security operators across Nigeria:
- Hausa (Northern Nigeria) - 50M+ speakers
- Yoruba (Southwestern Nigeria) - 40M+ speakers
- Igbo (Southeastern Nigeria) - 30M+ speakers
- Nigerian Pidgin English - 90M+ speakers
- English (Official)

Ensures accessibility and operational effectiveness for all Nigerian security personnel.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

app = FastAPI(
    title="🌍 Nigerian Language Support",
    version="1.0.0",
    description="Multi-Language Security Interface for National Inclusivity"
)

# ============================================================================
# LANGUAGE DEFINITIONS
# ============================================================================

class Language(str, Enum):
    ENGLISH = "en"
    HAUSA = "ha"
    YORUBA = "yo"
    IGBO = "ig"
    PIDGIN = "pcm"  # Nigerian Pidgin (ISO 639-3)

# ============================================================================
# SECURITY TRANSLATIONS
# ============================================================================

TRANSLATIONS = {
    # Dashboard & Navigation
    "dashboard": {
        Language.ENGLISH: "Dashboard",
        Language.HAUSA: "Allon Bayani",
        Language.YORUBA: "Ojú Ewè Àkóókò",
        Language.IGBO: "Ụlọ Ọrụ Mmalite",
        Language.PIDGIN: "Main Page"
    },
    "alerts": {
        Language.ENGLISH: "Alerts",
        Language.HAUSA: "Sanarwa",
        Language.YORUBA: "Ìkìlọ̀",
        Language.IGBO: "Ọkwa Ndị Nche",
        Language.PIDGIN: "Warnings Dem"
    },
    "security_map": {
        Language.ENGLISH: "Security Map",
        Language.HAUSA: "Taswirar Tsaro",
        Language.YORUBA: "Máàpù Ààbò",
        Language.IGBO: "Map Nchekwa",
        Language.PIDGIN: "Security Map"
    },
    
    # Threat Levels
    "threat_level": {
        Language.ENGLISH: "Threat Level",
        Language.HAUSA: "Matakin Barazana",
        Language.YORUBA: "Ìpele Ewu",
        Language.IGBO: "Ọkwa Ihe Egwu",
        Language.PIDGIN: "Danger Level"
    },
    "critical": {
        Language.ENGLISH: "CRITICAL",
        Language.HAUSA: "MAI MUHIMMANCI",
        Language.YORUBA: "PÁŃPÁŃŃDÁN",
        Language.IGBO: "IHE EGWU UKWU",
        Language.PIDGIN: "VERY SERIOUS"
    },
    "high": {
        Language.ENGLISH: "HIGH",
        Language.HAUSA: "BABBA",
        Language.YORUBA: "GÍGA",
        Language.IGBO: "ELU",
        Language.PIDGIN: "PLENTY"
    },
    "medium": {
        Language.ENGLISH: "MEDIUM",
        Language.HAUSA: "MATSAKAICI",
        Language.YORUBA: "ÀÁRÍN",
        Language.IGBO: "NKỊTỊ",
        Language.PIDGIN: "SMALL SMALL"
    },
    "low": {
        Language.ENGLISH: "LOW",
        Language.HAUSA: "KASA",
        Language.YORUBA: "KÉKERÉ",
        Language.IGBO: "NTA NTA",
        Language.PIDGIN: "SMALL"
    },
    
    # Actions & Commands
    "investigate": {
        Language.ENGLISH: "Investigate",
        Language.HAUSA: "Bincika",
        Language.YORUBA: "Ṣe Ìwádìí",
        Language.IGBO: "Chọpụta",
        Language.PIDGIN: "Check Am Well"
    },
    "respond": {
        Language.ENGLISH: "Respond",
        Language.HAUSA: "Amsa",
        Language.YORUBA: "Dáhùn",
        Language.IGBO: "Zaa",
        Language.PIDGIN: "Answer"
    },
    "escalate": {
        Language.ENGLISH: "Escalate",
        Language.HAUSA: "Haɓaka",
        Language.YORUBA: "Mú Ga Sókè",
        Language.IGBO: "Bulie Elu",
        Language.PIDGIN: "Make E Serious"
    },
    "dismiss": {
        Language.ENGLISH: "Dismiss",
        Language.HAUSA: "Wuce",
        Language.YORUBA: "Kọ̀ Sílẹ̀",
        Language.IGBO: "Wụpụ",
        Language.PIDGIN: "Leave Am"
    },
    
    # Security Events
    "intrusion_detected": {
        Language.ENGLISH: "Intrusion Detected",
        Language.HAUSA: "An Gano Kutse",
        Language.YORUBA: "Wíwọlé Tí Di Yíyẹ̀ Wò",
        Language.IGBO: "Achọpụtala Nbanye",
        Language.PIDGIN: "Somebody Wan Break Inside"
    },
    "phishing_attempt": {
        Language.ENGLISH: "Phishing Attempt",
        Language.HAUSA: "Yunkurin Ruɗu ta Yanar Gizo",
        Language.YORUBA: "Ìgbìyànjú Jíbìtì Alékún",
        Language.IGBO: "Nwalee Aghụghọ",
        Language.PIDGIN: "Scam Email"
    },
    "malware_detected": {
        Language.ENGLISH: "Malware Detected",
        Language.HAUSA: "An Gano Kwamfuta Mai Cutarwa",
        Language.YORUBA: "Kókó Ìbàjẹ́ Ti Di Yíyẹ̀ Wò",
        Language.IGBO: "Achọpụtala Malware",
        Language.PIDGIN: "Bad Software Dey"
    },
    "auth_anomaly": {
        Language.ENGLISH: "Authentication Anomaly",
        Language.HAUSA: "Matsalar Tabbatarwa",
        Language.YORUBA: "Ààbò Àwọn Ìdánimọ̀",
        Language.IGBO: "Nsogbu Njirimara",
        Language.PIDGIN: "Login Don Funny"
    },
    
    # System Status
    "operational": {
        Language.ENGLISH: "Operational",
        Language.HAUSA: "Yana Aiki",
        Language.YORUBA: "Ń Ṣiṣẹ́",
        Language.IGBO: "Na-arụ Ọrụ",
        Language.PIDGIN: "Dey Work"
    },
    "offline": {
        Language.ENGLISH: "Offline",
        Language.HAUSA: "Ba Aiki",
        Language.YORUBA: "Kò Ṣiṣẹ́",
        Language.IGBO: "Adịghị Arụ Ọrụ",
        Language.PIDGIN: "E No Dey Work"
    },
    "degraded": {
        Language.ENGLISH: "Degraded",
        Language.HAUSA: "Yana Raunana",
        Language.YORUBA: "Ń Bàjẹ́",
        Language.IGBO: "Ewelaghachi",
        Language.PIDGIN: "E Dey Manage"
    },
    
    # Personnel
    "officer": {
        Language.ENGLISH: "Officer",
        Language.HAUSA: "Jami'i",
        Language.YORUBA: "Ọ̀gágun",
        Language.IGBO: "Onye Uwe Ojii",
        Language.PIDGIN: "Officer"
    },
    "on_duty": {
        Language.ENGLISH: "On Duty",
        Language.HAUSA: "A Aiki",
        Language.YORUBA: "Lórí Iṣẹ́",
        Language.IGBO: "Na Ọrụ",
        Language.PIDGIN: "Dey Work Now"
    },
    "off_duty": {
        Language.ENGLISH: "Off Duty",
        Language.HAUSA: "Ba A Aiki",
        Language.YORUBA: "Kò Ṣiṣẹ́",
        Language.IGBO: "Adịghị Na Ọrụ",
        Language.PIDGIN: "No Dey Work"
    },
    
    # Infrastructure
    "pipeline": {
        Language.ENGLISH: "Pipeline",
        Language.HAUSA: "Bututun Mai",
        Language.YORUBA: "Páípù Èpo",
        Language.IGBO: "Ụzọ Mmanụ",
        Language.PIDGIN: "Pipe Line"
    },
    "railway": {
        Language.ENGLISH: "Railway",
        Language.HAUSA: "Hanyar Jirgin Ƙasa",
        Language.YORUBA: "Òpópónà Ọkọ̀ Ojú-Irin",
        Language.IGBO: "Ụzọ Ụgbọ Oloko",
        Language.PIDGIN: "Train Line"
    },
    "airport": {
        Language.ENGLISH: "Airport",
        Language.HAUSA: "Filin Jirgin Sama",
        Language.YORUBA: "Pápá Ọkọ̀ Òfúrufú",
        Language.IGBO: "Ọdụ Ụgbọ Elu",
        Language.PIDGIN: "Airport"
    },
    
    # Common Actions
    "search": {
        Language.ENGLISH: "Search",
        Language.HAUSA: "Bincika",
        Language.YORUBA: "Wá",
        Language.IGBO: "Chọọ",
        Language.PIDGIN: "Search"
    },
    "filter": {
        Language.ENGLISH: "Filter",
        Language.HAUSA: "Tace",
        Language.YORUBA: "Ṣẹ̀",
        Language.IGBO: "Họpụta",
        Language.PIDGIN: "Sort Out"
    },
    "export": {
        Language.ENGLISH: "Export",
        Language.HAUSA: "Fitar",
        Language.YORUBA: "Gbé Jáde",
        Language.IGBO: "Bupụta",
        Language.PIDGIN: "Carry Go Out"
    },
    "refresh": {
        Language.ENGLISH: "Refresh",
        Language.HAUSA: "Sabunta",
        Language.YORUBA: "Túnṣe",
        Language.IGBO: "Mee Ọhụrụ",
        Language.PIDGIN: "Update Am"
    },
    
    # Notifications
    "new_alert": {
        Language.ENGLISH: "New security alert",
        Language.HAUSA: "Sabon sanarwar tsaro",
        Language.YORUBA: "Ìkìlọ̀ Ààbò Tuntun",
        Language.IGBO: "Ọkwa Nchekwa Ọhụrụ",
        Language.PIDGIN: "New Security Warning"
    },
    "incident_resolved": {
        Language.ENGLISH: "Incident resolved",
        Language.HAUSA: "An magance matsala",
        Language.YORUBA: "Ọ̀ràn Ti Di Yíyanjú",
        Language.IGBO: "Edoziela Nsogbu",
        Language.PIDGIN: "Problem Don Finish"
    },
    "backup_needed": {
        Language.ENGLISH: "Backup needed",
        Language.HAUSA: "Ana buƙatar goyon baya",
        Language.YORUBA: "Ìrànwọ́ Ń Pọn Dandan",
        Language.IGBO: "Achọrọ Enyemaka",
        Language.PIDGIN: "We Need Help"
    }
}

# ============================================================================
# MODELS
# ============================================================================

class TranslationRequest(BaseModel):
    key: str = Field(..., description="Translation key")
    target_language: Language
    
class TranslationBatchRequest(BaseModel):
    keys: List[str]
    target_language: Language

class LocalizationConfig(BaseModel):
    user_id: str
    preferred_language: Language = Language.ENGLISH
    date_format: str = "DD/MM/YYYY"  # Nigerian standard
    time_format: str = "24h"
    timezone: str = "Africa/Lagos"  # WAT (West Africa Time)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/v1/translate")
async def translate(request: TranslationRequest) -> Dict[str, str]:
    """Translate a single key to target language"""
    if request.key not in TRANSLATIONS:
        return {
            "key": request.key,
            "translation": request.key,  # Fallback to key itself
            "language": request.target_language,
            "status": "not_found"
        }
    
    translations = TRANSLATIONS[request.key]
    translation = translations.get(
        request.target_language,
        translations.get(Language.ENGLISH, request.key)
    )
    
    return {
        "key": request.key,
        "translation": translation,
        "language": request.target_language,
        "status": "success"
    }

@app.post("/api/v1/translate/batch")
async def translate_batch(request: TranslationBatchRequest) -> Dict[str, Dict]:
    """Translate multiple keys at once"""
    results = {}
    
    for key in request.keys:
        if key in TRANSLATIONS:
            translations = TRANSLATIONS[key]
            results[key] = translations.get(
                request.target_language,
                translations.get(Language.ENGLISH, key)
            )
        else:
            results[key] = key  # Fallback
    
    return {
        "language": request.target_language,
        "translations": results,
        "count": len(results)
    }

@app.get("/api/v1/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {
                "code": Language.ENGLISH,
                "name": "English",
                "native_name": "English",
                "speakers": "200M+ (official)",
                "region": "National"
            },
            {
                "code": Language.HAUSA,
                "name": "Hausa",
                "native_name": "Hausa",
                "speakers": "50M+",
                "region": "Northern Nigeria"
            },
            {
                "code": Language.YORUBA,
                "name": "Yoruba",
                "native_name": "Yorùbá",
                "speakers": "40M+",
                "region": "Southwestern Nigeria"
            },
            {
                "code": Language.IGBO,
                "name": "Igbo",
                "native_name": "Ásụ̀sụ́ Ìgbò",
                "speakers": "30M+",
                "region": "Southeastern Nigeria"
            },
            {
                "code": Language.PIDGIN,
                "name": "Nigerian Pidgin",
                "native_name": "Naijá",
                "speakers": "90M+",
                "region": "National (informal)"
            }
        ],
        "total": 5
    }

@app.get("/api/v1/translations/all/{language}")
async def get_all_translations(language: Language):
    """Get all translations for a specific language"""
    result = {}
    
    for key, translations in TRANSLATIONS.items():
        result[key] = translations.get(
            language,
            translations.get(Language.ENGLISH, key)
        )
    
    return {
        "language": language,
        "translations": result,
        "count": len(result)
    }

@app.post("/api/v1/localization/config")
async def set_user_localization(config: LocalizationConfig):
    """Set user localization preferences"""
    # In production, save to user profile database
    return {
        "status": "success",
        "user_id": config.user_id,
        "config": config.dict()
    }

@app.get("/api/v1/localization/detect")
async def detect_language_from_region(state: str):
    """Suggest language based on Nigerian state"""
    # Map of Nigerian states to primary languages
    state_languages = {
        # Northern States (Hausa)
        "kano": Language.HAUSA,
        "kaduna": Language.HAUSA,
        "katsina": Language.HAUSA,
        "sokoto": Language.HAUSA,
        "zamfara": Language.HAUSA,
        "kebbi": Language.HAUSA,
        "jigawa": Language.HAUSA,
        "bauchi": Language.HAUSA,
        "gombe": Language.HAUSA,
        
        # Southwestern States (Yoruba)
        "lagos": Language.YORUBA,
        "oyo": Language.YORUBA,
        "ogun": Language.YORUBA,
        "osun": Language.YORUBA,
        "ondo": Language.YORUBA,
        "ekiti": Language.YORUBA,
        "kwara": Language.YORUBA,
        
        # Southeastern States (Igbo)
        "anambra": Language.IGBO,
        "enugu": Language.IGBO,
        "ebonyi": Language.IGBO,
        "imo": Language.IGBO,
        "abia": Language.IGBO,
        
        # Mixed/Other (default to English + Pidgin)
        "rivers": Language.PIDGIN,
        "delta": Language.PIDGIN,
        "abuja": Language.ENGLISH,
    }
    
    suggested_language = state_languages.get(
        state.lower(),
        Language.ENGLISH
    )
    
    return {
        "state": state,
        "suggested_language": suggested_language,
        "alternatives": [Language.ENGLISH, Language.PIDGIN]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "operational",
        "service": "nigerian-language-support",
        "supported_languages": 5,
        "translation_keys": len(TRANSLATIONS)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8102)
