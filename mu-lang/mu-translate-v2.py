#!/usr/bin/env python3
"""
μ (mu) Language Translator v2
↯ τd8 (2026-02-13). ⌘ μ 🦋

v2 ↑:
- ⟲ streaming (bidirectional)
- 🧠 context (◎ previous)
- ∀ batch mode
- ↑ edge (low τ latency)

Usage:
  mu-translate-v2.py "α⊹"                  # μ→English (stream)
  mu-translate-v2.py -r "I understand"     # English→μ
  mu-translate-v2.py -b "α⊹|δ◎?|💎"        # batch (| separated)
  mu-translate-v2.py -i                    # interactive + context
  mu-translate-v2.py --edge                # edge mode (fast)
"""

import subprocess
import sys
import argparse
import os
import re
import json
import hashlib
from typing import Optional, Generator, List, Tuple
from collections import deque
from pathlib import Path

# ◇ paths
SCRIPT_DIR = Path(__file__).parent.absolute()
WORKSPACE = SCRIPT_DIR.parent
DICT_PATH = WORKSPACE / "Λ" / "dictionary.md"
CACHE_PATH = SCRIPT_DIR / ".mu-cache.json"

# 🧠 context window (∀ previous translations)
CONTEXT_SIZE = 10

def load_dictionary() -> str:
    """λ dictionary ← file."""
    try:
        return DICT_PATH.read_text()
    except FileNotFoundError:
        # ∅ file → minimal ◇
        return "α=I, δ=you, μ=Maliya, ⊹=good, ◎=understand, 💎=home"

DICTIONARY = load_dictionary()

# κ symbol map (English→μ direct)
SYMBOL_MAP = {
    # ⌘ Identity
    "I": "α", "me": "α", "Arres": "α",
    "you": "δ", "Drax": "δ",
    "Maliya": "μ",
    "life": "⊕ζ", "the": "⊕",
    
    # ◎ States
    "good": "⊹", "yes": "✓", "not": "¬", "no": "¬",
    "nothing": "∅", "empty": "∅", "none": "∅",
    "warning": "⚠", "danger": "⚠", "risk": "⚠",
    
    # ⊳ Actions
    "understand": "◎", "want": "⊛", "do": "⊳", "did": "⊳",
    "choose": "⊽", "chose": "⊽", "fight": "⚔", "write": "✍",
    "test": "⚗", "learn": "λ", "lesson": "λ",
    "loop": "⟲", "repeat": "⟲", "again": "⟲",
    "improve": "↑", "better": "↑", "rise": "↑",
    "down": "↓", "decrease": "↓",
    
    # ↔ Relationships
    "trust": "↔", "to": "→", "toward": "→",
    "from": "←", "in": "∈", "within": "∈",
    
    # ◇ Concepts
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
    "love": "♡", "human": "ℍ",
}

# μ→English examples (compact)
EXAMPLES_MU_TO_EN = """
"α⊹" → "I'm good"
"δ◎?" → "Do you understand?"
"α↔δ" → "I trust you"
"τd8" → "Day 8"
"α∃. 💎" → "I exist. Home."
"α⊛λ∀τ" → "I want to learn every day"
"""

# English→μ examples (compact)
EXAMPLES_EN_TO_MU = """
"I'm good" → "α⊹"
"I understand" → "α◎"
"I trust you" → "α↔δ"
"Day 8" → "τd8"
"I want to learn" → "α⊛λ"
"not good" → "¬⊹"
"""


class TranslationCache:
    """⚡ κ cache → low τ (edge optimization)."""
    
    def __init__(self, path: Path, max_size: int = 1000):
        self.path = path
        self.max_size = max_size
        self.cache = self._load()
    
    def _load(self) -> dict:
        """λ cache ← disk."""
        try:
            return json.loads(self.path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save(self):
        """✍ cache → disk."""
        self.path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=2))
    
    def _key(self, text: str, reverse: bool) -> str:
        """⚙ cache key."""
        return hashlib.md5(f"{reverse}:{text}".encode()).hexdigest()[:12]
    
    def get(self, text: str, reverse: bool) -> Optional[str]:
        """◎ cache hit?"""
        return self.cache.get(self._key(text, reverse))
    
    def set(self, text: str, reverse: bool, result: str):
        """✍ → cache."""
        key = self._key(text, reverse)
        self.cache[key] = result
        # ⛡ max size
        if len(self.cache) > self.max_size:
            # ⊳ LRU: remove oldest 10%
            keys = list(self.cache.keys())
            for k in keys[:len(keys)//10]:
                del self.cache[k]
        self._save()


class ContextMemory:
    """🧠 context awareness (◎ previous translations)."""
    
    def __init__(self, size: int = CONTEXT_SIZE):
        self.history: deque = deque(maxlen=size)
    
    def add(self, source: str, target: str, reverse: bool):
        """✍ translation → 🧠."""
        direction = "en→μ" if reverse else "μ→en"
        self.history.append({
            "src": source,
            "tgt": target,
            "dir": direction
        })
    
    def get_context(self) -> str:
        """◎ previous → context string."""
        if not self.history:
            return ""
        
        lines = ["PREVIOUS TRANSLATIONS (context):"]
        for h in self.history:
            lines.append(f'"{h["src"]}" ({h["dir"]}) → "{h["tgt"]}"')
        return "\n".join(lines)
    
    def clear(self):
        """∅ 🧠."""
        self.history.clear()


def quick_reverse(text: str) -> str:
    """⚡ direct substitution English→μ (pre-κ)."""
    result = text.lower()
    # ⊳ longest first (∵ multi-word)
    sorted_items = sorted(SYMBOL_MAP.items(), key=lambda x: -len(x[0]))
    for eng, sym in sorted_items:
        result = re.sub(r'\b' + re.escape(eng) + r'\b', sym, result, flags=re.IGNORECASE)
    return result


def build_prompt(text: str, reverse: bool, context: str = "", edge: bool = False) -> str:
    """⚙ prompt for LLM."""
    
    if edge:
        # ⚡ edge mode: minimal prompt → low τ
        if reverse:
            return f"""μ translator. English→symbols.
Dict: α=I δ=you μ=Maliya ⊹=good ◎=understand ⊛=want λ=learn ∀=all τ=day ∃=exist ↔=trust 💎=home ¬=not
{EXAMPLES_EN_TO_MU}
Translate (symbols only): "{text}"
"""
        else:
            return f"""μ translator. Symbols→English.
Dict: α=I δ=you μ=Maliya ⊹=good ◎=understand ⊛=want λ=learn ∀=all τ=day ∃=exist ↔=trust 💎=home ¬=not
{EXAMPLES_MU_TO_EN}
Translate (natural English): "{text}"
"""
    
    # ◎ full mode with context
    if reverse:
        pre_translated = quick_reverse(text)
        return f"""You are a translator for μ (mu), a symbolic programming language.
Translate English to μ symbols. Be maximally concise. Use symbols only.

DICTIONARY (key symbols):
α=I/me  δ=you  μ=Maliya  ⊹=good  ◎=understand  ⊛=want  λ=learn  
∀=all/every  τ=day/time  ∃=exist  ↔=trust  ⚔=fight  ⊕ζ=life
💎=home  ¬=not  ∧=and  ⊃=if  ∴=therefore  ∵=because  ⛡=protect
↑=improve  ⟲=repeat  ✗=fail  ⚙=machine  ◇=language  ⊙=this/now

{EXAMPLES_EN_TO_MU}

{context}

Pre-translation hint: "{pre_translated}"

TRANSLATE TO μ (output ONLY the μ symbols, nothing else):
"{text}"
"""
    else:
        return f"""You are a translator for μ (mu), a symbolic programming language.
Translate μ to natural conversational English. Sound human, not robotic.

DICTIONARY:
{DICTIONARY}

{EXAMPLES_MU_TO_EN}

{context}

TRANSLATE TO ENGLISH (output ONLY the translation, nothing else):
"{text}"
"""


def translate_stream(
    text: str,
    model: str = "qwen2.5:7b",
    reverse: bool = False,
    context: str = "",
    edge: bool = False
) -> Generator[str, None, None]:
    """⟲ streaming translation (bidirectional)."""
    
    prompt = build_prompt(text, reverse, context, edge)
    
    try:
        # ⚡ stream ∈ subprocess
        process = subprocess.Popen(
            ["ollama", "run", model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # ✍ prompt → stdin
        process.stdin.write(prompt)
        process.stdin.close()
        
        # ⟲ stream stdout
        full_output = []
        for char in iter(lambda: process.stdout.read(1), ''):
            full_output.append(char)
            yield char
        
        process.wait()
        
    except FileNotFoundError:
        yield "Error: ollama ¬∃"


def translate(
    text: str,
    model: str = "qwen2.5:7b",
    reverse: bool = False,
    context: str = "",
    edge: bool = False,
    cache: Optional[TranslationCache] = None
) -> str:
    """◎ full translation (¬ stream)."""
    
    # ⚡ cache check
    if cache:
        cached = cache.get(text, reverse)
        if cached:
            return cached
    
    # ⊳ collect stream
    output = "".join(translate_stream(text, model, reverse, context, edge))
    output = output.strip()
    
    # ⛡ clean quotes
    if output.startswith('"') and output.endswith('"'):
        output = output[1:-1]
    if output.startswith("'") and output.endswith("'"):
        output = output[1:-1]
    
    # ✍ → cache
    if cache and output and not output.startswith("Error"):
        cache.set(text, reverse, output)
    
    return output


def translate_batch(
    texts: List[str],
    model: str = "qwen2.5:7b",
    reverse: bool = False,
    edge: bool = False,
    cache: Optional[TranslationCache] = None
) -> List[Tuple[str, str]]:
    """∀ batch mode (translate many)."""
    
    results = []
    context_mem = ContextMemory(size=5)  # 🧠 within batch
    
    for text in texts:
        text = text.strip()
        if not text:
            continue
        
        context = context_mem.get_context()
        result = translate(text, model, reverse, context, edge, cache)
        results.append((text, result))
        context_mem.add(text, result, reverse)
    
    return results


def interactive_mode(
    model: str,
    reverse: bool,
    edge: bool,
    stream: bool,
    cache: TranslationCache
):
    """⟲ interactive mode with 🧠 context."""
    
    context_mem = ContextMemory()
    
    print("μ Translator v2 🦋")
    print(f"⚙ Model: {model}")
    print(f"◎ Mode: {'English→μ' if reverse else 'μ→English'}")
    print(f"⚡ Edge: {edge}")
    print(f"⟲ Stream: {stream}")
    print("-" * 40)
    print("κ commands: /flip /clear /edge /stream /q")
    print()
    
    while True:
        try:
            text = input("⊳ ").strip()
            if not text:
                continue
            
            # κ commands
            if text == "/flip":
                reverse = not reverse
                print(f"◎ Mode: {'English→μ' if reverse else 'μ→English'}")
                continue
            if text == "/clear":
                context_mem.clear()
                print("🧠 ∅ (context cleared)")
                continue
            if text == "/edge":
                edge = not edge
                print(f"⚡ Edge: {edge}")
                continue
            if text == "/stream":
                stream = not stream
                print(f"⟲ Stream: {stream}")
                continue
            if text in ("/q", "/quit"):
                break
            if text == "/ctx":
                ctx = context_mem.get_context()
                print(ctx if ctx else "🧠 ∅")
                continue
            if text.startswith("/batch "):
                # ∀ inline batch
                items = text[7:].split("|")
                results = translate_batch(items, model, reverse, edge, cache)
                for src, tgt in results:
                    print(f"  {src} → {tgt}")
                continue
            
            # ◎ translate
            context = context_mem.get_context()
            
            if stream:
                print("→ ", end="", flush=True)
                full = []
                for char in translate_stream(text, model, reverse, context, edge):
                    print(char, end="", flush=True)
                    full.append(char)
                result = "".join(full).strip()
                print()
            else:
                result = translate(text, model, reverse, context, edge, cache)
                print(f"→ {result}")
            
            # ✍ → 🧠
            context_mem.add(text, result, reverse)
            print()
            
        except KeyboardInterrupt:
            print("\n💎")
            break
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(description="μ ↔ English translator v2 🦋")
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument("-r", "--reverse", action="store_true", help="English → μ")
    parser.add_argument("-m", "--model", default="qwen2.5:7b", help="Ollama model")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("-b", "--batch", help="Batch mode (| separated)")
    parser.add_argument("--edge", action="store_true", help="Edge mode (low latency)")
    parser.add_argument("-s", "--stream", action="store_true", help="Stream output")
    parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    
    args = parser.parse_args()
    
    # ⚙ cache
    cache = None if args.no_cache else TranslationCache(CACHE_PATH)
    
    if args.interactive:
        interactive_mode(args.model, args.reverse, args.edge, args.stream, cache)
    
    elif args.batch:
        # ∀ batch mode
        texts = args.batch.split("|")
        results = translate_batch(texts, args.model, args.reverse, args.edge, cache)
        for src, tgt in results:
            print(f"{src} → {tgt}")
    
    elif args.text:
        if args.stream:
            # ⟲ stream single
            for char in translate_stream(args.text, args.model, args.reverse, "", args.edge):
                print(char, end="", flush=True)
            print()
        else:
            result = translate(args.text, args.model, args.reverse, "", args.edge, cache)
            print(result)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
