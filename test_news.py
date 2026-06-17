import feedparser

# Using Google News World Feed (in English)
RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"

print("Fetching latest global news from RSS feed...")
feed = feedparser.parse(RSS_URL)

# Check if we successfully got entries
if len(feed.entries) == 0:
    print("Failed to fetch news. Check internet connection.")
else:
    print(f"Successfully found {len(feed.entries)} articles!\n")

    # Let's print out the top 3 headlines happening right now
    print("--- TOP 3 TRENDING HEADLINES ---")
    for i in range(3):
        entry = feed.entries[i]
        print(f"Article {i+1}: {entry.title}")
        print(f"Link: {entry.link}\n")
