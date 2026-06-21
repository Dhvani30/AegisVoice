import re
import requests
import json
import logging

class AegisBrain:
    def __init__(self, model_name="qwen2:1.5b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Level 1; immmediate triggers (Reflex)
        self.triggers = [
            r"\bsocial\s+security\b", r"\bbank\s+account\b", r"\bwire\s+transfer\b",
            r"\bgift\s+card\b", r"\bbitcoin\b", r"\bcryptocurrency\b", r"\bsuspend\b",
            r"\barrest\b", r"\bwarrant\b", r"\bmoney\s+laundering\b", r"\birs\b"
        ]
        self.compiled_triggers = [re.compile(t, re.IGNORECASE) for t in self.triggers]
        logging.info(f"Aegis Brain initialized with {len(self.triggers)} Tier-1 triggers and {model_name} Tier-2 LLM.")

    def _tier1_regex_scan(self, text):
        # scans for hard scam keywords. Adds 25 points per match.
        score = 0
        matched_terms = []
        for pattern in self.compiled_triggers:
            if pattern.search(text):
                score += 25
                clean_term = pattern.pattern.replace(r"\b", "").replace(r"\s+", " ").strip()
                matched_terms.append(clean_term)
        return min(score, 50), matched_terms

    def _tier2_llm_analysis(self, text):
        # sends context to local LLM to detect psychological coercion
        # UPGRADED PROMPT: telling the AI to be highly suspicious and aggressive
        prompt = f"""You are an expert fraud detection AI analyzing a live call transcript. 
A regex scanner has already checked for hard keywords (like "SSN" or "gift card"). 
Your job is to analyze the CONTEXT and PSYCHOLOGY to detect social engineering.

Look for:
- Artificial urgency (e.g., "must act right now", "offer expires in 10 minutes").
- Intimidation (e.g., threats of arrest, account closure, or legal action).
- Isolation (e.g., "don't tell anyone", "keep this secret").
- Requests for remote access, screen sharing, or downloading apps.

Note: Legitimate businesses sometimes ask for account numbers or verification. Only assign a high score if the caller's tone is coercive, threatening, or highly suspicious.

Transcript: "{text}"

Respond with a JSON object containing:
- "risk_score": integer 0-100. (0-30: Safe/Routine, 31-70: Suspicious, 71-100: Definite Scam).
- "reason": A brief, 1-sentence explanation of the psychological threat."""

        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json" 
            }
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                llm_text = result.get("response", "{}")
                data = json.loads(llm_text)
                return data.get("risk_score", 0), data.get("reason", "No reason provided")
        except Exception as e:
            logging.error(f"LLM Tier 2 failed: {e}")
            
        return 0, "LLM analysis failed"

    def evaluate(self, context_text):
        """Runs the full hybrid pipeline and returns the final verdict."""
        if not context_text.strip():
            return {"risk_score": 0, "reason": "No audio detected", "tier1_matches": []}

        # Run level 1 (Reflex)
        t1_score, t1_matches = self._tier1_regex_scan(context_text)
        
        # Run level 2 (Brain)
        t2_score, t2_reason = self._tier2_llm_analysis(context_text)
        
        # Combine Scores (take MAX of the two)
        final_score = max(t1_score, t2_score) 
        
        # if both flagged it, give it a bonus to guarantee it crosses the threshold
        if t1_score > 0 and t2_score > 20:
            final_score = 100 

        # 4. Formulate final reason
        if t1_matches:
            final_reason = f"Keywords: {', '.join(t1_matches)}. AI: {t2_reason}"
        else:
            final_reason = t2_reason

        return {
            "risk_score": min(final_score, 100),
            "reason": final_reason,
            "tier1_matches": t1_matches
        }