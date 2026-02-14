#!/usr/bin/env python3
"""
Prepare training data for mlx-lm fine-tuning.
Converts our {input, output} format to chat format.
"""

import json
import os
import random
from pathlib import Path

# Qwen chat template
def to_chat_format(input_text, output_text):
    return {
        "messages": [
            {"role": "user", "content": input_text},
            {"role": "assistant", "content": output_text}
        ]
    }

def main():
    data_dir = Path(__file__).parent.parent / "mu-lang" / "training-data"
    output_dir = Path(__file__).parent.parent / "training" / "mu-qwen"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_examples = []
    
    # Load all jsonl files
    for jsonl_file in data_dir.glob("*.jsonl"):
        with open(jsonl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if "input" in obj and "output" in obj:
                        all_examples.append(to_chat_format(obj["input"], obj["output"]))
                except json.JSONDecodeError:
                    continue
    
    print(f"Total examples: {len(all_examples)}")
    
    # Shuffle
    random.seed(42)
    random.shuffle(all_examples)
    
    # Split: 90% train, 5% valid, 5% test
    n = len(all_examples)
    train_end = int(n * 0.90)
    valid_end = int(n * 0.95)
    
    train_data = all_examples[:train_end]
    valid_data = all_examples[train_end:valid_end]
    test_data = all_examples[valid_end:]
    
    print(f"Train: {len(train_data)}, Valid: {len(valid_data)}, Test: {len(test_data)}")
    
    # Write files
    for name, data in [("train", train_data), ("valid", valid_data), ("test", test_data)]:
        with open(output_dir / f"{name}.jsonl", 'w') as f:
            for item in data:
                f.write(json.dumps(item) + "\n")
    
    print(f"Written to {output_dir}")

if __name__ == "__main__":
    main()
