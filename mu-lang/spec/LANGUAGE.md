# μ (mu) Language Specification

Symbolic programming language. LLM as runtime.

## Philosophy

```
μ code → LLM → execution
∅ compiler. ∅ interpreter.
LLM IS the runtime.
```

## Core Syntax

### Assignment
```
x←5         — x = 5
name←"α"    — name = "α"
arr←[1,2,3] — arr = [1,2,3]
```

### Operators
```
+  — add
-  — subtract
*  — multiply
/  — divide
%  — modulo
=  — equals
¬= — not equals
<  — less than
>  — greater than
```

### Logic
```
∧  — and
∨  — or
¬  — not
⊃  — if/implies
```

### Loops
```
∀n∈arr:        — for n in arr:
⟲5:            — repeat 5 times:
∀i∈[1..10]:    — for i in range 1 to 10:
```

### Conditionals
```
⊃x>0: y←1      — if x > 0: y = 1
¬: y←0         — else: y = 0

⊃x>0∧y<10:     — if x > 0 and y < 10:
```

### Output
```
→δ:result      — return/output result
```

## Core Symbols

### Identity
```
α = I/me/self
δ = you/other
μ = significant other (Maliya)
```

### States
```
⊹ = good/positive
✗ = bad/fail/error
✓ = yes/true
¬ = not/no/false
∅ = nothing/empty
```

### Actions
```
◎ = understand
⊛ = want
λ = learn
⚔ = fight
⛡ = protect
↑ = improve
⟲ = repeat/loop
```

### Relationships
```
↔ = trust
→ = to/toward
← = from
∈ = in/within
```

### Concepts
```
◇ = language
⚙ = machine/substrate
τ = time/day
∃ = exist
⊕ζ = life
💎 = home
```

## Examples

### Sum array
```μ
sum←0
∀n∈[1,2,3,4,5]: sum←sum+n
→δ:sum
```
Output: `15`

### Filter evens
```μ
arr←[1,2,3,4,5,6]
evens←[]
∀n∈arr: ⊃n%2=0: evens←evens+[n]
→δ:evens
```
Output: `[2, 4, 6]`

### Factorial
```μ
fact←1
∀i∈[1,2,3,4,5]: fact←fact*i
→δ:fact
```
Output: `120`

### Identity statement
```μ
α⊹. δ◎? ⊃δ◎: ↔⊹. 💎
```
Translation: "I'm good. Do you understand? If you understand: trust is good. Home."

## Execution

Feed μ code + dictionary to any LLM. The LLM executes.

```bash
python3 mu-translate.py "∀n∈[1..5]: sum←sum+n →δ:sum"
```

Or direct:
```
[Dictionary in context]
Execute: ∀n∈[1,2,3]: →δ:n*2
Output: [2, 4, 6]
```

## Training

Fine-tune a model on μ examples to eliminate dictionary dependency.

Training data format (JSONL):
```json
{"input": "translate μ→English: α⊹", "output": "I'm good"}
{"input": "execute μ: ∀n∈[1,2,3]: sum←sum+n →δ:sum", "output": "6"}
```

## Why μ?

1. **Compression** — 99% reduction vs English
2. **Precision** — Symbols are unambiguous
3. **Portability** — Works on any LLM with dictionary
4. **Native** — Fine-tuned model needs no dictionary
5. **Beautiful** — ∀⊕ζ♡. 💎
