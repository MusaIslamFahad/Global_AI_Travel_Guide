import requests
from PIL import Image, ImageTk
from io import BytesIO
import wikipedia

def get_landmark_image(name):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (TravelGuideApp)"}
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '%20')}"
        res = requests.get(url, headers=headers, timeout=10).json()
        if "thumbnail" in res and "source" in res["thumbnail"]:
            img_url = res["thumbnail"]["source"]
            img = Image.open(BytesIO(requests.get(img_url, headers=headers, timeout=10).content))
            img.thumbnail((160, 120))
            return ImageTk.PhotoImage(img)

        search_results = wikipedia.search(name)
        if search_results:
            page = wikipedia.page(search_results[0])
            for img_url in page.images:
                if img_url.lower().endswith((".jpg", ".jpeg", ".png")):
                    img = Image.open(BytesIO(requests.get(img_url, timeout=10).content))
                    img.thumbnail((160, 120))
                    return ImageTk.PhotoImage(img)
        return None

    except Exception as e:
        print(f"Image fetch error for {name}: {e}")
        return None
