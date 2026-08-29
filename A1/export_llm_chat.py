import json
import os

log_file = '/home/jdsb/.gemini/antigravity/brain/e4f20c24-9886-4d61-9b7c-8ff33e56ef4c/.system_generated/logs/transcript_full.jsonl'
output_file = 'LLM_Conversations.md'

with open(log_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
out.append("# LLM Conversation Log\n")
out.append("This document contains the complete record of user prompts and AI assistant responses for ADBMS Assignment 0 & 1.\n\n---\n")

step_num = 1
for line in lines:
    try:
        data = json.loads(line)
        stype = data.get('type', '')
        source = data.get('source', '')
        content = data.get('content', '')

        if stype == 'USER_INPUT' or source == 'USER_EXPLICIT':
            out.append(f"## Step {step_num}: USER PROMPT\n\n```text\n{content.strip()}\n```\n\n")
            step_num += 1
        elif stype == 'PLANNER_RESPONSE' or source == 'MODEL':
            if content:
                out.append(f"### AI ASSISTANT RESPONSE\n\n{content.strip()}\n\n---\n")
    except Exception:
        continue

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(''.join(out))

print(f"LLM Conversation Log successfully saved to {output_file} ({len(lines)} log lines processed).")
