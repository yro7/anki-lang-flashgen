import requests
from duckduckgo_search import DDGS

def get(query: str) -> bytes | None:
    """
    Search for an image on DuckDuckGo for the given word and return the bytes.
    Returns None if no image is found or in case of an error.
    """
    if not query:
        return None

    print(f"   🖼️  Searching for image for: '{query}'...")

    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query=query,
                max_results=1,
                safesearch="on"
            ))
            
            if not results:
                print(f"      ⚠️ No image found for '{query}'.")
                return None
            
            image_url = results[0]['image']
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            response = requests.get(image_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"      ⚠️ Download error (Code {response.status_code})")
                return None

    except Exception as e:
        print(f"      ❌ Image API Error : {e}")
        return None

if __name__ == "__main__":
    mot = "Pomme rouge"
    image_bytes = get(mot)
    
    if image_bytes:
        print(f"✅ Image retrieved successfully ({len(image_bytes)} bytes)")
        with open("test_image.jpg", "wb") as f:
            f.write(image_bytes)
    else:
        print("❌ Retrieval failed.")