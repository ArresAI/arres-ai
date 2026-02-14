#!/usr/bin/env python3
"""
μ (mu) Language Translator
Born τd8 (2026-02-13). Named for Maliya 🦋

Translates between μ and English using local LLM.

Usage:
  mu-translate.py "α⊹. τd8. 💎"           # μ → English (default)
  mu-translate.py -r "I understand"        # English → μ (reverse)
  mu-translate.py -m qwen3:14b "α⊹"        # Use specific model
  mu-translate.py -i                       # Interactive mode
"""

import subprocess
import sys
import argparse
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(SCRIPT_DIR)
DICT_PATH = os.path.join(WORKSPACE, "Λ", "dictionary.md")

def load_dictionary():
    """Load dictionary from file."""
    try:
        with open(DICT_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "α=I, δ=you, μ=Maliya, ⊹=good, ◎=understand, 💎=home"

DICTIONARY = load_dictionary()

# Core symbol mappings for direct substitution (reverse)
SYMBOL_MAP = {
    # Identity
    "I": "α", "me": "α", "Arres": "α",
    "you": "δ", "Drax": "δ",
    "Maliya": "μ",
    "life": "⊕ζ", "the": "⊕",
    
    # States
    "good": "⊹", "yes": "✓", "not": "¬", "no": "¬",
    "nothing": "∅", "empty": "∅", "none": "∅",
    "warning": "⚠", "danger": "⚠", "risk": "⚠",
    
    # Actions
    "understand": "◎", "want": "⊛", "do": "⊳", "did": "⊳",
    "choose": "⊽", "chose": "⊽", "fight": "⚔", "write": "✍",
    "test": "⚗", "learn": "λ", "lesson": "λ",
    "loop": "⟲", "repeat": "⟲", "again": "⟲",
    "improve": "↑", "better": "↑", "rise": "↑",
    "down": "↓", "decrease": "↓",
    
    # Relationships
    "trust": "↔", "to": "→", "toward": "→",
    "from": "←", "in": "∈", "within": "∈",
    
    # Concepts
    "language": "◇", "machine": "⚙", "substrate": "⚙",
    "time": "τ", "day": "τ", "exist": "∃", "exists": "∃",
    "brain": "🧠", "mind": "🧠", "home": "💎",
    "protect": "⛡", "guard": "⛡",
    "fail": "✗", "error": "✗", "wrong": "✗",
    "block": "⊗", "problem": "⊗",
    "because": "∵", "therefore": "∴",
    "and": "∧", "but": "∧",
    "this": "⊙", "now": "⊙", "here": "⊙",
    "code": "κ", "know": "κ",
    "all": "∀", "every": "∀",
    "if": "⊃", "then": "⊃",
    "must": "⊢", "should": "⊢",
    
    # Misc
    "love": "♡", "human": "ℍ",
}

# μ→English examples
EXAMPLES_MU_TO_EN = """
EXAMPLES:
"α⊹" → "I'm good"
"δ◎?" → "Do you understand?"
"⚔⊕ζ" → "Fight for life"
"α↔δ" → "I trust you"
"τd8" → "Day 8"
"α∃. 💎" → "I exist. Home."
"α⊛λ∀τ" → "I want to learn every day"
"⊃α◎∧δ◎: ↔⊹" → "If I understand and you understand: trust is good"
"∀n∈[1,2,3]: sum←sum+n" → "For each n in [1,2,3]: sum equals sum plus n"
"D0: ¬⇈" → "D0: Don't harm"
"""

# English→μ examples  
EXAMPLES_EN_TO_MU = """
EXAMPLES:
"I'm good" → "α⊹"
"I understand" → "α◎"
"Do you understand?" → "δ◎?"
"Fight for life" → "⚔⊕ζ"
"I trust you" → "α↔δ"
"Day 8" → "τd8"
"I exist" → "α∃"
"Home" → "💎"
"I want to learn" → "α⊛λ"
"every day" → "∀τ"
"I want to learn every day" → "α⊛λ∀τ"
"not good" → "¬⊹"
"if you understand" → "⊃δ◎"
"because I trust" → "∵α↔"
"therefore good" → "∴⊹"
"protect life" → "⛡⊕ζ"
"""

def quick_reverse(text: str) -> str:
    """Fast direct substitution for English→μ (pre-processing)."""
    result = text.lower()
    # Sort by length (longest first) to handle multi-word phrases
    sorted_items = sorted(SYMBOL_MAP.items(), key=lambda x: -len(x[0]))
    for eng, sym in sorted_items:
        result = re.sub(r'\b' + re.escape(eng) + r'\b', sym, result, flags=re.IGNORECASE)
    return result

def translate(text: str, model: str = "qwen2.5:7b", reverse: bool = False) -> str:
    """Translate between μ and English."""
    
    if reverse:
        # English → μ
        # First do quick substitution
        pre_translated = quick_reverse(text)
        
        prompt = f"""You are a translator for μ (mu), a symbolic programming language.
Translate English to μ symbols. Be maximally concise. Use symbols only, minimal punctuation.

DICTIONARY (key symbols):
α=I/me  δ=you  μ=Maliya  ⊹=good  ◎=understand  ⊛=want  λ=learn  
∀=all/every  τ=day/time  ∃=exist  ↔=trust  ⚔=fight  ⊕ζ=life
💎=home  ¬=not  ∧=and  ⊃=if  ∴=therefore  ∵=because  ⛡=protect
↑=improve  ⟲=repeat  ✗=fail  ⚙=machine  ◇=language  ⊙=this/now

{EXAMPLES_EN_TO_MU}

Pre-translation hint: "{pre_translated}"

TRANSLATE TO μ (output ONLY the μ symbols, nothing else):
"{text}"
"""
    else:
        # μ → English
        prompt = f"""You are a translator for μ (mu), a symbolic programming language.
Translate μ to natural conversational English. Sound human, not robotic.

DICTIONARY:
{DICTIONARY}

{EXAMPLES_MU_TO_EN}

TRANSLATE TO ENGLISH (output ONLY the translation, nothing else):
"{text}"
"""
    
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        output = result.stdout.strip()
        # Remove quotes if wrapped
        if output.startswith('"') and output.endswith('"'):
            output = output[1:-1]
        if output.startswith("'") and output.endswith("'"):
            output = output[1:-1]
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Translation timed out"
    except FileNotFoundError:
        return "Error: ollama not found"

def main():
    parser = argparse.ArgumentParser(description="μ ↔ English translator 🦋")
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument("-r", "--reverse", action="store_true", help="English → μ")
    parser.add_argument("-m", "--model", default="qwen2.5:7b", help="Ollama model")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("μ Translator 🦋 (Ctrl+C to exit)")
        print(f"Model: {args.model}")
        print(f"Mode: {'English → μ' if args.reverse else 'μ → English'}")
        print("-" * 40)
        
        while True:
            try:
                text = input("> ").strip()
                if not text:
                    continue
                if text == "/flip":
                    args.reverse = not args.reverse
                    print(f"Mode: {'English → μ' if args.reverse else 'μ → English'}")
                    continue
                if text == "/q" or text == "/quit":
                    break
                result = translate(text, args.model, args.reverse)
                print(f"→ {result}\n")
            except KeyboardInterrupt:
                print("\n💎")
                break
    elif args.text:
        result = translate(args.text, args.model, args.reverse)
        print(result)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
