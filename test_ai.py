from services.ai_service import ask_gemini

response = ask_gemini(
    "Say hello. Reply in one sentence only."
)

print(response)