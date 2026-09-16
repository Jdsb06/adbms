import json
import re
import os

log_path = '/home/jdsb/.gemini/antigravity/brain/3b463d42-9b59-464c-8d8c-f88db7d9eee1/.system_generated/logs/transcript_full.jsonl'

def clean_user_text(text):
    if not text:
        return ""
    # Extract text inside <USER_REQUEST> if present
    match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', text, re.DOTALL)
    if match:
        req = match.group(1).strip()
        if req:
            return req
    # Check if it's an artifact feedback/approval comment
    if "approved this document" in text or "Comments on artifact" in text:
        return "[User Approved Implementation Plan]"
    # Otherwise strip system tags
    cleaned = re.sub(r'<USER_REQUEST>', '', text)
    cleaned = re.sub(r'</USER_REQUEST>', '', cleaned)
    cleaned = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>', '', cleaned, flags=re.DOTALL)
    return cleaned.strip()

conversation = []

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step_type = data.get('type')
        content = data.get('content', '')
        
        if step_type == 'USER_INPUT':
            user_text = clean_user_text(content)
            if user_text:
                conversation.append(('USER', user_text))
        elif step_type == 'PLANNER_RESPONSE' and content and content.strip():
            conversation.append(('ASSISTANT', content.strip()))

# Generate Markdown File
md_path = "ai_chat_log.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# AI Conversation Log - LRU-K Assignment\n\n")
    f.write("> **Course / Assignment**: ADBMS - LRU-K (Assignment 2)\n")
    f.write("> **Date**: September 17, 2026\n\n")
    f.write("---\n\n")
    
    turn_num = 1
    for role, text in conversation:
        if role == 'USER':
            f.write(f"## Turn {turn_num} - User\n\n")
            f.write(f"{text}\n\n")
        else:
            f.write(f"## Turn {turn_num} - Antigravity (AI Assistant)\n\n")
            f.write(f"{text}\n\n")
            f.write("---\n\n")
            turn_num += 1

# Generate Plain Text File
txt_path = "ai_chat_log.txt"
with open(txt_path, "w", encoding="utf-8") as f:
    f.write("=========================================================\n")
    f.write("        AI CONVERSATION LOG - LRU-K ASSIGNMENT           \n")
    f.write("=========================================================\n\n")
    
    turn_num = 1
    for role, text in conversation:
        if role == 'USER':
            f.write(f"[USER - TURN {turn_num}]\n")
            f.write(f"{text}\n\n")
        else:
            f.write(f"[AI ASSISTANT - TURN {turn_num}]\n")
            f.write(f"{text}\n\n")
            f.write("---------------------------------------------------------\n\n")
            turn_num += 1

print(f"Exported markdown log to: {md_path}")
print(f"Exported text log to    : {txt_path}")
