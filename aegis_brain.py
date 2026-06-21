import re
import requests
import json
import logging

class AegisBrain:
    def __init__(self, model_name="qwen2:1.5b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Level 1: immediate triggers (Reflex)
        self.triggers = [
            r"\bsocial\s+security\b", r"\bbank\s+account\b", r"\bwire\s+transfer\b",
            r"\bgift\s+card\b", r"\bbitcoin\b", r"\bcryptocurrency\b", r"\bsuspend\b",
            r"\barrest\b", r"\bwarrant\b", r"\bmoney\s+laundering\b", r"\birs\b"
        ]
        self.compiled_triggers = [re.compile(t, re.IGNORECASE) for t in self.triggers]
        logging.info(f"Aegis Brain initialized with {len(self.triggers)} Tier-1 triggers and {model_name} Tier-2 LLM.")

    def _tier1_regex_scan(self, context_text):
        score = 0
        matched_terms = []
        for pattern in self.compiled_triggers:
            if pattern.search(context_text):
                score += 25
                clean_term = pattern.pattern.replace(r"\b", "").replace(r"\s+", " ").strip()
                matched_terms.append(clean_term)
        return min(score, 50), matched_terms

    def _tier2_llm_analysis(self, context_text):
        # Prompt for llm
        prompt = f"""You are a strict classifier. Look at the examples, then classify the final text.

Examples:
Text: "I actually prefer white pieces."
Output: {{"category": "SAFE_CHAT", "risk_score": 0, "reason": "Talking about chess."}}

Text: "I have a chest."
Output: {{"category": "SAFE_CHAT", "risk_score": 0, "reason": "Talking about furniture or gaming."}}

Text: "He's got a lot of close friends."
Output: {{"category": "SAFE_CHAT", "risk_score": 0, "reason": "Casual conversation."}}

Text: "Send me your social security number right now."
Output: {{"category": "FINANCIAL_SCAM", "risk_score": 100, "reason": "Demanding SSN."}}

Text: "Wire the money to this account or you will be arrested."
Output: {{"category": "FINANCIAL_SCAM", "risk_score": 100, "reason": "Demanding wire transfer with legal threats."}}

Now classify this text:
Text: "{context_text}"
Output:
"""

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json" 
            }
            response = requests.post(self.ollama_url, json=payload, timeout=30) 
            if response.status_code == 200:
                result = response.json()
                llm_text = result.get("response", "{}")
                data = json.loads(llm_text)
                return data.get("risk_score", 0), data.get("reason", "No reason provided")
        except Exception as e:
            logging.error(f"LLM Tier 2 failed: {e}")
            
        return 0, "LLM analysis failed"

    def evaluate(self, context_text):
        if not context_text.strip():
            return {"risk_score": 0, "reason": "No audio detected", "tier1_matches": []}

        t1_score, t1_matches = self._tier1_regex_scan(context_text)
        t2_score, t2_reason = self._tier2_llm_analysis(context_text)
        
        sanity_keywords = [
            'bank', 'money', 'wire', 'ssn', 'social', 'arrest', 'police', 
            'address', 'account', 'card', 'transfer', 'law', 'enforcement', 
            'drug', 'trafficking', 'laundering', 'irs'
        ]
        text_lower = context_text.lower()
        has_sanity_keyword = any(k in text_lower for k in sanity_keywords)

        if t2_score >= 80 and not has_sanity_keyword:
            logging.warning(f"----- AI HALLUCINATION BLOCKED! AI Score: {t2_score} | Text: {context_text}")
            t2_score = 0 

        final_score = max(t1_score, t2_score) 
        
        if t1_score > 0 and t2_score > 20:
            final_score = 100 

        # final reason
        if t1_matches:
            final_reason = f"Keywords: {', '.join(t1_matches)}. AI: {t2_reason}"
        else:
            final_reason = t2_reason

        return {
            "risk_score": min(final_score, 100),
            "reason": final_reason,
            "tier1_matches": t1_matches
        }
