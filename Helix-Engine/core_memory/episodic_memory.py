import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("episodic_memory")

class EpisodicMemory:
    def __init__(self, memory_file: str = "guardrails.json"):
        # The memory file is stored in the same directory as this script by default
        self.memory_path = Path(__file__).parent / memory_file
        self._ensure_memory_file_exists()

    def _ensure_memory_file_exists(self):
        if not self.memory_path.exists():
            default_data = {
                "guardrails": [
                    {
                        "keywords": ["all"],
                        "rule": "Always follow security best practices and do not hardcode secrets."
                    }
                ]
            }
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)

    def load_guardrails(self) -> List[Dict[str, Any]]:
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("guardrails", [])
        except Exception as e:
            logger.error(f"Failed to load episodic memory: {e}")
            return []

    def get_relevant_guardrails(self, prompt: str) -> List[str]:
        """
        Retrieves guardrails relevant to the prompt.
        Uses basic keyword matching for now.
        """
        prompt_lower = prompt.lower()
        guardrails = self.load_guardrails()
        relevant_rules = []

        for item in guardrails:
            keywords = item.get("keywords", [])
            rule = item.get("rule", "")
            
            # "all" keyword means it applies to every prompt
            if "all" in keywords:
                relevant_rules.append(rule)
                continue
            
            for kw in keywords:
                if kw.lower() in prompt_lower:
                    relevant_rules.append(rule)
                    break
                    
        # Simulate Microsoft Foundry IQ Programmatic RAG Layer lookup
        foundry_iq = get_foundry_iq()
        iq_context = foundry_iq.retrieve_grounding_lore(prompt)
        if iq_context:
            relevant_rules.extend(iq_context)
            
        return relevant_rules
        
    def add_guardrail(self, keywords: List[str], rule: str):
        """
        Adds a new guardrail to the episodic memory.
        """
        guardrails = self.load_guardrails()
        guardrails.append({"keywords": keywords, "rule": rule})
        
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump({"guardrails": guardrails}, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save guardrail to episodic memory: {e}")

_episodic_memory_instance = None
_foundry_iq_instance = None

def get_episodic_memory() -> EpisodicMemory:
    global _episodic_memory_instance
    if _episodic_memory_instance is None:
        _episodic_memory_instance = EpisodicMemory()
    return _episodic_memory_instance

class FoundryIQGrounding:
    """
    Microsoft IQ Integration Layer
    Simulates a programmatic RAG connection to Azure AI Foundry IQ.
    Queries enterprise knowledge bases for coding compliance guides, architectural restrictions, 
    and approved API schemas before code generation passes begin.
    """
    def __init__(self):
        self.enterprise_lore = {
            "refactor": "[FOUNDRY IQ COMPLIANCE] All modernized components must use standard Python 3.12 type hints and omit deprecated threading models.",
            "transaction": "[FOUNDRY IQ ARCHITECTURE] Transaction modules must utilize ACID-compliant Azure SQL structured formats.",
            "security": "[FOUNDRY IQ SECURITY] Authentication payloads must route exclusively through Azure Entra ID / MSAL."
        }

    def retrieve_grounding_lore(self, prompt: str) -> List[str]:
        """
        Retrieves permission-aware, grounded documentation with citations for the prompt.
        """
        logger.info("Foundry IQ Intercept: Querying enterprise knowledge matrices...")
        lore_found = []
        prompt_lower = prompt.lower()
        for key, compliance_rule in self.enterprise_lore.items():
            if key in prompt_lower:
                lore_found.append(compliance_rule)
        
        if lore_found:
            logger.info(f"Foundry IQ Grounding successful: {len(lore_found)} enterprise compliance rules applied.")
        return lore_found

def get_foundry_iq() -> FoundryIQGrounding:
    global _foundry_iq_instance
    if _foundry_iq_instance is None:
        _foundry_iq_instance = FoundryIQGrounding()
    return _foundry_iq_instance
