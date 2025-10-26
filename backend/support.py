from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

RESOURCES: List[Dict[str, str]] = [
    {
        "name": "National Domestic Violence Hotline (US)",
        "type": "emergency",
        "phone": "1-800-799-7233",
        "chat": "https://www.thehotline.org/",
        "notes": "Available 24/7 for crisis counseling, safety planning, and referrals.",
    },
    {
        "name": "National Sexual Assault Hotline (RAINN - US)",
        "type": "emergency",
        "phone": "1-800-656-4673",
        "chat": "https://hotline.rainn.org/online",
        "notes": "Confidential support for sexual assault survivors.",
    },
    {
        "name": "Women's Aid (UK)",
        "type": "support",
        "phone": "0808 2000 247",
        "chat": "https://chat.womensaid.org.uk/",
        "notes": "24/7 support line and live chat for women experiencing abuse.",
    },
    {
        "name": "Financial Abuse Support (Purple Purse)",
        "type": "financial",
        "url": "https://www.thehotline.org/plan-for-safety/finances/",
        "notes": "Guidance on financial safety planning and regaining control of finances.",
    },
    {
        "name": "Emergency Services",
        "type": "emergency",
        "phone": "911",
        "notes": "If you are in immediate danger, please call emergency services right away.",
    },
]


@dataclass
class RiskResult:
    level: str
    triggers: List[str]
    recommended_resources: List[Dict[str, str]]


RISK_KEYWORDS = {
    "immediate_danger": [
        "immediate danger",
        "right now",
        "hurt me",
        "threatening",
        "weapon",
        "strangling",
        "choking",
        "killing",
    ],
    "high": [
        "stalking",
        "controlled",
        "tracking",
        "locked",
        "nowhere",
        "terrified",
        "scared",
        "trapped",
        "financial abuse",
        "money",
        "bank account",
        "credit",
        "took my card",
        "stole my paycheck",
    ],
    "moderate": [
        "isolated",
        "verbal",
        "insults",
        "controlling",
        "angry",
        "monitoring",
        "jealous",
        "gaslight",
        "intimidate",
    ],
}

RISK_ORDER = ["unknown", "low", "moderate", "high", "immediate_danger"]


def merge_risk_levels(current: str, new: str) -> str:
    current_index = RISK_ORDER.index(current) if current in RISK_ORDER else 0
    new_index = RISK_ORDER.index(new) if new in RISK_ORDER else 0
    return RISK_ORDER[max(current_index, new_index)]


def assess_risk(message: str) -> RiskResult:
    lowered = message.lower()
    triggers: List[str] = []
    level = "low"

    for risk_level, keywords in RISK_KEYWORDS.items():
        found = [kw for kw in keywords if kw in lowered]
        if found:
            triggers.extend(found)
            if risk_level == "immediate_danger":
                level = "immediate_danger"
                break
            elif risk_level == "high" and level not in {"immediate_danger", "high"}:
                level = "high"
            elif risk_level == "moderate" and level not in {"immediate_danger", "high", "moderate"}:
                level = "moderate"

    recommended = [res for res in RESOURCES if res["type"] in {"emergency", "support"}]
    if level in {"high", "immediate_danger"}:
        recommended = [res for res in RESOURCES if res["type"] == "emergency"]
    elif level == "moderate":
        recommended = [res for res in RESOURCES if res["type"] in {"support", "financial"}]
    else:
        recommended = RESOURCES.copy()

    return RiskResult(level=level, triggers=triggers, recommended_resources=recommended)


def build_supportive_message(risk: RiskResult) -> str:
    base = (
        "I'm really sorry that you're going through this. "
        "Your safety and well-being are the most important things right now."
    )

    if risk.level == "immediate_danger":
        guidance = (
            " If you are in immediate danger, please contact emergency services (such as 911) "
            "or a trusted person nearby as soon as possible."
        )
    elif risk.level == "high":
        guidance = (
            " I hear how serious this situation is. Reaching out to a crisis hotline or advocate "
            "can help you create a safety plan tailored to what you're facing."
        )
    elif risk.level == "moderate":
        guidance = (
            " It may help to document what is happening and connect with a local advocate who "
            "can support you."
        )
    else:
        guidance = (
            " Thank you for sharing this with me. If you're comfortable, consider connecting "
            "with a support organization that can listen and help you explore options."
        )

    reminder = (
        " If you need to quickly close this page, remember to clear your browser history or use "
        "a safe device whenever possible."
    )

    return base + guidance + reminder
