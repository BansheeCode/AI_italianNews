from google import genai

# Initialize the new modern client with your key
client = genai.Client(
    api_key="AQ.Ab8RN6IqkaPFTwebs40ApesE-v7zcr6vMoBya8laySBWhzoegQ")

# Our test headline
news_headline = "Scientists discover a new species of marine life in the deep Pacific Ocean."

# The system prompt instructing the multi-level output
prompt = f"""
Take the following news headline and create a multi-level reading exercise for Italian learners. 
Provide the output in clean Markdown format with the following sections:

## A1 (Principiante)
- A maximum of 30 words in very simple Italian (Present tense only).
- A short vocabulary list with English translations.

## B1 (Intermedio)
- A paragraph of 60-80 words in natural, standard Italian.
- Include a mix of present and past tenses (passato prossimo).

Headline to process: {news_headline}
"""

print("Sending to Gemini... Please wait...")

# Calling the correct, updated model via the new SDK syntax
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("\n--- AI RESPONSE ---")
print(response.text)
