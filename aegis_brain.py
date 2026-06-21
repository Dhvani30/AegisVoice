import re
import requests
import json
import logging

class AegisBrain:
    def __init__(self, model_name="qwen2:1.5b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # TIER 1: Hard triggers (The "Reflex")
        self.triggers = [
            r"\bsocial\s+security\b", r"\bbank\s+account\b", r"\bwire\s+transfer\b",
            r"\bgift\s+card\b", r"\bbitcoin\b", r"\bcryptocurrency\b", r"\bsuspend\b",
            r"\barrest\b", r"\bwarrant\b", r"\bmoney\s+laundering\b", r"\birs\b"
        ]
        self.compiled_triggers = [re.compile(t, re.IGNORECASE) for t in self.triggers]
        logging.info(f"🧠 Aegis Brain initialized with {len(self.triggers)} Tier-1 triggers and {model_name} Tier-2 LLM.")

    def _tier1_regex_scan(self, full_context):
        score = 0
        matched_terms = []
        for pattern in self.compiled_triggers:
            if pattern.search(full_context):
                score += 25
                clean_term = pattern.pattern.replace(r"\b", "").replace(r"\s+", " ").strip()
                matched_terms.append(clean_term)
        return min(score, 50), matched_terms

    def _tier2_llm_analysis(self, latest_chunk):
        # STRICT SORTING HAT PROMPT - Now analyzing ONLY the latest chunk
        prompt = f"""You are a strict classifier. Look at the examples, then classify the final text.

CRITICAL RULES:
1. You MUST respond ONLY in English.
2. If the text is fragmented, incomplete, or unclear, classify it as SAFE_CHAT with risk_score 0.
3. Do not hallucinate threats from incomplete sentences.

Examples:
Text: "I actually prefer white pieces."
Output: {{"category": "SAFE_CHAT", "risk_score": 0, "reason": "Talking about chess."}}

Text: "It's not possible. Okay. But even if the sh-"
Output: {{"category": "SAFE_CHAT", "risk_score": 0, "reason": "Incomplete sentence about shipping."}}

Text: "Send me your social security number right now."
Output: {{"category": "FINANCIAL_SCAM", "risk_score": 100, "reason": "Demanding SSN."}}

Text: "Do you want it or not? I'm the one with the money right now."
Output: {{"category": "FINANCIAL_SCAM", "risk_score": 100, "reason": "Demanding money with coercion."}}

Now classify this text:
Text: "{latest_chunk}"
Output:"""

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
                
                # extracting reason
                reason = data.get("reason", "No reason provided")
                
                # check if it's ASCII
                if not reason.isascii():
                    logging.warning(f" NON-ENGLISH HALLUCINATION BLOCKED! Reason: {reason}")
                    return 0, "Language guardrail blocked non-English output"
                
                return data.get("risk_score", 0), reason
        except Exception as e:
            logging.error(f"LLM Tier 2 failed: {e}")
            
        return 0, "LLM analysis failed"

    def evaluate(self, full_context, latest_chunk):
        if not full_context.strip():
            return {"risk_score": 0, "reason": "No audio detected", "tier1_matches": []}

        # run level 1 (Reflex) on FULL CONTEXT
        t1_score, t1_matches = self._tier1_regex_scan(full_context)
        
        # run level 2 (Brain) on LATEST CHUNK
        t2_score, t2_reason = self._tier2_llm_analysis(latest_chunk)
        
        # level 3 THE ANTI-HALLUCINATION GUARDRAIL
        sanity_keywords = [
            'bank', 'money', 'wire', 'ssn', 'social', 'arrest', 'police', 
            'address', 'account', 'card', 'transfer', 'law', 'enforcement', 
            'drug', 'trafficking', 'laundering', 'irs'
        ]
        text_lower = full_context.lower()
        has_sanity_keyword = any(k in text_lower for k in sanity_keywords)
        
        if t2_score >= 80 and not has_sanity_keyword:
            logging.warning(f"AI HALLUCINATION BLOCKED! AI Score: {t2_score} | Text: {latest_chunk}")
            t2_score = 0

        # level 4 scoring logic
        # If Regex found a keyword (t1_score > 0) AND LLM confirms it's a scam (t2_score >= 50), 
        # then it's a definite scam.
        if t1_score > 0 and t2_score >= 50:
            final_score = 100
        else:
            # Otherwise, take the max of the two scores
            final_score = max(t1_score, t2_score)

        # 5. Formulate final reason
        if t1_matches:
            final_reason = f"Keywords: {', '.join(t1_matches)}. AI: {t2_reason}"
        else:
            final_reason = t2_reason

        return {
            "risk_score": min(final_score, 100),
            "reason": final_reason,
            "tier1_matches": t1_matches
        }