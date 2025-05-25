import getpass
import os
import json

from langchain_openai import AzureChatOpenAI

from app.utils.pptx_generator import generate_slides
from app.llm.prompt_templates import CHAT_PROMPT_TEMPLATE


def ensure_api_key():
    """
    Check if Azure OpenAI API key is set in environment variables.
    If not, prompt the user to enter it securely.
    """
    if not os.environ.get("AZURE_OPENAI_API_KEY"):
        os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter API key for Azure: ")


# Initialize LLM client with Azure OpenAI configuration from environment variables
def init_llm() -> AzureChatOpenAI:
    """
    Initialize AzureChatOpenAI client with environment variables.
    """
    return AzureChatOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

def generate_outline(user_input: str, llm: AzureChatOpenAI) -> list:
    """
    Generate a presentation outline in JSON format from a user prompt using LLM.

    Args:
        prompt_text (str): User input prompt describing the presentation topic.
        llm (AzureChatOpenAI): Initialized AzureChatOpenAI client.

    Returns:
        list: Parsed JSON list of slide outlines.
    """
    prompt = CHAT_PROMPT_TEMPLATE.invoke({"prompt": user_input})
    response = llm.invoke(prompt)
    content = response.content

    # Parse JSON from AI response string
    outline = json.loads(content)
    return outline


def main():
    """
    Main function to generate presentation outline JSON, save it,
    and generate PPTX slides from the outline.
    """
    ensure_api_key()
    llm = init_llm()

    user_prompt = "Create me presentation about Python."

    # Generate slide outline JSON from prompt
    slide_outline = generate_outline(user_prompt, llm)

    print("Generated outline JSON:")
    print(json.dumps(slide_outline, indent=2))

    # Save JSON outline to file
    json_filename = "presentation_outline.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(slide_outline, f, indent=2, ensure_ascii=False)

    print(f"Outline JSON saved to '{json_filename}'.")

    # Generate and save PPTX slides based on outline
    generate_slides(slide_num=len(slide_outline), slide_content=slide_outline)


if __name__ == "__main__":
    main()
