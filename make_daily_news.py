import feedparser
import trafilatura
from google import genai
from google.genai import types
from datetime import datetime
import time

# 1. Configuration
API_KEY = "AQ.Ab8RN6IqkaPFTwebs40ApesE-v7zcr6vMoBya8laySBWhzoegQ"
RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

# Initialize our AI client
client = genai.Client(api_key=API_KEY)

print("Step 1: Fetching live global news feed...")
feed = feedparser.parse(RSS_URL)

if len(feed.entries) == 0:
    print("Error: Could not read news feed.")
    exit()

NUMBER_OF_ARTICLES = 3
today_articles_data = []

print(
    f"Extracting the top {NUMBER_OF_ARTICLES} articles and downloading full text...")
for i in range(min(NUMBER_OF_ARTICLES, len(feed.entries))):
    article = feed.entries[i]
    url = article.link

    # Use trafilatura to download the actual article text safely
    print(f" -> Fetching full text for: {article.title[:50]}...")
    downloaded = trafilatura.fetch_url(url)
    article_body = trafilatura.extract(
        downloaded) if downloaded else "No article body text could be retrieved."

    today_articles_data.append({
        "title": article.title,
        "link": url,
        # Cap text at 3000 characters to keep requests clean
        "body": article_body[:3000]
    })

# 2. General, Professional System Prompt (No hardcoded rules!)
SYSTEM_INSTRUCTION = f"""
You are an expert linguistic professor and native Italian journalist. Your task is to analyze an English news headline along with its accompanying full article text, extract the core factual events, and rewrite them into multi-level reading exercises for students learning Italian.

CRITICAL FACTUAL AND GROUNDING RULES:
- The current year is {datetime.today().year}. Ensure all political, social, and chronological contexts reflect this accurately.
- You must rely strictly on the real context provided in the article text and your real-time grounding capabilities. Do not hallucinate historical data or make up facts that conflict with the current reality.
- Maintain journalistic objectivity.

For the headline and text provided, you must output exactly three levels (A1, A2, B1) using this exact Markdown template:

### 🟢 Livello A1 (Principiante)
- A 2-3 sentence summary of the factual event. 
- Keep it to a A1 CEFR level (trying to push to an early A2 though)
- GRAMMAR RULES: Use ONLY high-frequency basic vocabulary, strict PRESENT TENSE verbs (do not use passato prossimo or past tenses), and simple subject-verb-object syntax. Maximum 40 words.
- **Vocabolario A1:** A bulleted list of 3 basic Italian nouns or verbs used in the text with their English translations.

### 🟡 Livello A2 (Elementare)
- A 4-5 sentence summary. 
- CEFR level A2
- GRAMMAR RULES: Introduce simple past tenses (passato prossimo) and basic conjunctions (ma, perché, quando, quindi) to connect ideas. Maximum 60 words.
- **Vocabolario A2:** A bulleted list of 2 useful expressions or words used in the text with their English translations.

### 🟠 Livello B1 (Intermedio)
- A detailed paragraph of 80-100 words written in standard, elegant, and natural Italian journalism style (not overly complex though). Use a mix of compound sentences, varying tenses (including imperfetto and futuro if appropriate), and diverse vocabulary.
- **Vocabolario B1:** A bulleted list of 2 advanced vocabulary words or phrases used in the text with their English translations.
- CEFR level B1

---
"""

# Build the official config object with instructions and Google Search Grounding
ai_config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=[types.Tool(google_search=types.GoogleSearch())]
)

# 3. Process the articles through the AI
all_news_content = f"# Giornale del Giorno: {datetime.today().strftime('%d/%m/%Y')}\n\n"

print("\nStep 2: Sending complete data packages to Gemini...")
for idx, art in enumerate(today_articles_data):
    print(f" Processing Article {idx+1}: {art['title']}")

    # Now we pass BOTH the headline and the actual raw body text to the prompt context!
    user_prompt = f"""
    HEADLINE: {art['title']}
    ORIGINAL SOURCE LINK: {art['link']}
    FULL ARTICLE TEXT CONTEXT: 
    {art['body']}
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=ai_config
            )

            all_news_content += f"## {idx+1}. Summary of: {art['title']}\n"
            all_news_content += f"*Fonte originale in inglese: [Link all'articolo]({art['link']})*\n\n"
            all_news_content += str(response.text) + "\n\n"
            break

        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                print(
                    f"      ⚠️ Google servers busy. Retrying in 5 seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(5)
            else:
                print(f"      ❌ Failed to process article due to error: {e}")
                all_news_content += f"## {idx+1}. Error processing story\n*Could not generate text for this headline due to downtime.*\n\n"
                break

# 4. Save everything to a single daily file
today_date = datetime.today().strftime('%Y-%m-%d')
filename = f"{today_date}.md"

print(f"\nStep 3: Saving all 3 data-grounded articles to '{filename}'...")
with open(filename, "w", encoding="utf-8") as file:
    file.write(all_news_content)

print("\n🎉 Success! Check your folder for the beautifully accurate markdown file!")
