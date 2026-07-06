from google import genai
from config import GEMINI_API_KEY

# Instantiate official Google GenAI execution engine core client
client = genai.Client(api_key=GEMINI_API_KEY)

def ask_gemini(prompt: str, system_instruction: str = None) -> str:
    try:
        # Execute streaming prompt payload construction mapping instructions cleanly
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"system_instruction": system_instruction} if system_instruction else None
        )
        if response and response.text:
            return response.text
        return "Error: Received empty response from generative model infrastructure."
    except Exception as e:
        print(f"GEMINI ENGINE ERROR: API call failed: {str(e)}")
        return "System Error: The underlying generative AI engine encountered an unexpected state error."