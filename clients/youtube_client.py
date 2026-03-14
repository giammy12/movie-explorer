import requests
from config import YOUTUBE_API_KEY
from exceptions import APIError

class YouTubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3/search"

    def search_trailer(self, title, year):
        query = f"{title} {year} official trailer"

        params ={
            "key": YOUTUBE_API_KEY,
            "q": query,
            "part" : "snippet",
            "type": "video",
            "maxResults" : 5
        }

        response = requests.get(self.BASE_URL, params=params, timeout=10)

        if response.status_code != 200:
            raise APIError("Errore nella richiesta Youtube")
        
        data = response.json()

        items = data.get("items", [])
        if not items:
            return None
        
        first_item = items[0]
        video_id = first_item["id"] ["videoId"]
        trailer_title = first_item["snippet"] ["title"]
        trailer_url = f"https://www.youtube.com/watch?v={video_id}"

        return{
            "video_id" : video_id,
            "title" : trailer_title,
            "url" : trailer_url
        }
    
