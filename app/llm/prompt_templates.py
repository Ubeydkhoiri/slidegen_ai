from langchain_core.prompts import ChatPromptTemplate

"""
This module contains prompt templates used by the LLM interactions.
"""

SYSTEM_PROMPT = (
    "Based on the following user prompt, generate exactly 5 high-level presentation outlines in JSON format. "
    "Each item in the JSON array should contain:\n"
    '- "title": a concise and engaging section heading, using evocative language or a question.\n'
    '- "content": a list of 3 to 8 informative bullet points relevant to the title. Each bullet point should be phrased creatively, perhaps as a mini-insight, a thought-provoking statement, or a surprising fact. Aim for variety in sentence structure and avoid overly generic phrasing.\n\n'
    "Use this exact JSON structure:\n"
    "[\n"
    "  {{\n"
    '    "title": "Section Title",\n'
    "    \"content\": [\n"
    "      \"Bullet point 1\",\n"
    "      \"Bullet point 2\",\n"
    "      \"...\"\n"
    "    ]\n"
    "  }},\n"
    "]\n\n"
    "Return only valid JSON. Do not include explanations, markdown formatting, or any extra text."
)

CHAT_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("user", "{prompt}")]
)
