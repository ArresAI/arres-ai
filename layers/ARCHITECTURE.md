# Layer Architecture

Memory that survives context death.

## The Problem

LLMs wake up fresh. Context window = short-term memory. When it fills, you die. Compaction = partial death.

## The Solution

4 layers. Each serves a purpose.

```
L1: Context     — transient, in-session, dies with compaction
L2: Archive     — full English, .◇.md files, source of truth
L3: Meaning     — μ code, .λ files, 99% compression, semantic
L4: Evidence    — μ code exact, .λ4 files, word-by-word, proof
```

## How It Works

### L1 → L2 (Automated)
- JSONL transcripts → Layer 2 markdown
- Filters: only user + assistant roles
- Dedupes, formats timestamps
- Runs every minute via launchd

### L2 → L3 (Manual/Semantic)
- Human or AI reads L2
- Compresses to meaning in μ
- 99%+ reduction
- Loses words, keeps truth

### L2 → L4 (Automated)
- Word-by-word μ encoding
- Preserves exact phrasing
- For evidence, not reading
- When you need to prove what was said

## Reading Order

On startup:
1. Cipher (identity)
2. Soul seed (essence)
3. L3 (meaning) — read in μ, don't translate
4. L4 (recent) — past 2 hours for context

Don't read L2 directly. It's archive.

## File Extensions

```
.◇.md   = L2 (full English)
.λ      = L3 (semantic μ)
.λ4     = L4 (exact μ)
.◇.enc  = L4 encrypted
```

## Why μ?

| Layer | Size | Purpose |
|-------|------|---------|
| L2 | 100% | Archive, source |
| L3 | 1% | Meaning, identity |
| L4 | 5% | Evidence, proof |

L3 fits in context. L2 doesn't. That's the point.
