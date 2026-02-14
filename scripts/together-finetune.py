#!/usr/bin/env python3
"""
Fine-tune Qwen on μ using Together.ai
"""

import json
import os
from together import Together

client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

# Convert to Together chat format
def convert_to_together_format(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if "input" in obj and "output" in obj:
                    chat = {
                        "messages": [
                            {"role": "user", "content": obj["input"]},
                            {"role": "assistant", "content": obj["output"]}
                        ]
                    }
                    f_out.write(json.dumps(chat) + "\n")
            except json.JSONDecodeError:
                continue

# Convert data
print("Converting training data...")
convert_to_together_format("/tmp/mu-all-training.jsonl", "/tmp/mu-together.jsonl")

# Count lines
with open("/tmp/mu-together.jsonl", 'r') as f:
    count = sum(1 for _ in f)
print(f"Total examples: {count}")

# Upload file
print("Uploading to Together.ai...")
file_resp = client.files.upload(
    file="/tmp/mu-together.jsonl",
    purpose="fine-tune"
)
print(f"File ID: {file_resp.id}")

# Start fine-tune
print("Starting fine-tune...")
ft_resp = client.fine_tuning.create(
    training_file=file_resp.id,
    model="Qwen/Qwen2.5-7B-Instruct",
    n_epochs=3,
    learning_rate=1e-5,
    suffix="mu-v1"
)

print(f"Fine-tune job ID: {ft_resp.id}")
print(f"Status: {ft_resp.status}")
print("💎")
