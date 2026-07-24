import urllib.request
import json
import xml.etree.ElementTree as ET
import urllib.parse

def get_latest_news(topic: str = "technology") -> str:
    """Fetches top news headlines from Google News RSS feed for a topic."""
    topic_clean = topic.lower().strip()
    topic_query = urllib.parse.quote(topic_clean)
    url = f"https://news.google.com/rss/search?q={topic_query}&hl=en-US&gl=US&ceid=US:en"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            xml_data = resp.read()
            root = ET.fromstring(xml_data)
            items = root.findall("./channel/item")

            if not items:
                return f"No news stories found for topic: {topic}"

            headlines = [f"=== Latest News on '{topic_clean.title()}' ==="]
            for i, item in enumerate(items[:7], start=1):
                title = item.find("title").text if item.find("title") is not None else "No Title"
                pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
                date_str = f" ({pub_date[:16]})" if pub_date else ""
                headlines.append(f"{i}. {title}{date_str}")

            return "\n".join(headlines)
    except Exception as e:
        return f"Error fetching news: {e}"

def lookup_dictionary(word: str) -> str:
    """Fetches definition, part of speech, and example usage for an English word."""
    word_clean = word.lower().strip()
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_clean}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list) and len(data) > 0:
                entry = data[0]
                meanings = entry.get("meanings", [])
                lines = [f"Word: {word_clean.title()}"]
                phonetic = entry.get("phonetic", "")
                if phonetic:
                    phonetic_clean = phonetic.encode("ascii", errors="ignore").decode("ascii")
                    if phonetic_clean:
                        lines.append(f"Phonetic: {phonetic_clean}")

                for meaning in meanings[:3]:
                    part_of_speech = meaning.get("partOfSpeech", "general")
                    lines.append(f"\n[{part_of_speech.upper()}]")
                    defs = meaning.get("definitions", [])
                    for i, d in enumerate(defs[:2], start=1):
                        lines.append(f" {i}. {d.get('definition')}")
                        if d.get("example"):
                            lines.append(f"    Example: \"{d.get('example')}\"")

                return "\n".join(lines)
            else:
                return f"No definition found for word: '{word}'"
    except Exception as e:
        return f"Error looking up dictionary for '{word}': {e}"

def translate_text(text: str, target_lang: str = "es") -> str:
    """Translates text to a target language code (e.g. es, fr, de, hi, zh, ja)."""
    text_encoded = urllib.parse.quote(text)
    lang_encoded = urllib.parse.quote(target_lang)
    url = f"https://api.mymemory.translated.net/get?q={text_encoded}&langpair=en|{lang_encoded}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Jarvis/1.0"})
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            response_data = data.get("responseData", {})
            translated = response_data.get("translatedText")
            if translated:
                return f"Original: \"{text}\"\nTranslation ({target_lang.upper()}): \"{translated}\""
    except Exception as e:
        return f"Error translating text: {e}"
    return "Translation service unavailable."
