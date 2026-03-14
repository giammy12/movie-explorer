import requests
from config import OMDB_API_KEY
from exceptions import InvalidResponseError, APIError, NotFoundError

class OMDBClient:
    BASE_URL = "http://www.omdbapi.com/"

    def search_by_title(self, title):

        params ={
        "apikey": OMDB_API_KEY,
        "t": title
        }

        response = requests.get(self.BASE_URL, params=params, timeout=10)
        if response.status_code != 200:
            raise APIError("Errore nella richiesta OMDb")
    
        data = response.json()
        
        if data.get("Response") == "False":
            raise NotFoundError(data.get("Error", "Film non trovato") )
    
        if "Title" not in data or "Year" not in data:
            raise InvalidResponseError("Risposta OMDb non valida")
            
    
        return data
    
    def search_many_by_title(self, title):
        params = {
            "apikey": OMDB_API_KEY,
            "s": title
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
        except requests.RequestException as error:
            raise APIError(f"Errore di connessione a OMDb: {error}")

        if response.status_code != 200:
            raise APIError("Errore nella richiesta OMDb")

        try:
            data = response.json()
        except ValueError:
            raise InvalidResponseError("La risposta di OMDb non è un JSON valido")

        if data.get("Response") == "False":
            raise NotFoundError(data.get("Error", "Nessun risultato trovato"))

        results = data.get("Search", [])
        return results
    
    def search_by_imdb_id(self, imdb_id):
        params = {
            "apikey": OMDB_API_KEY,
            "i": imdb_id
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
        except requests.RequestException as error:
            raise APIError(f"Errore di connessione a OMDb: {error}")

        if response.status_code != 200:
            raise APIError("Errore nella richiesta OMDb")

        try:
            data = response.json()
        except ValueError:
            raise InvalidResponseError("La risposta di OMDb non è un JSON valido")

        if data.get("Response") == "False":
            raise NotFoundError(data.get("Error", "Film non trovato"))

        if "Title" not in data or "Year" not in data:
            raise InvalidResponseError("Risposta OMDb non valida")

        return data