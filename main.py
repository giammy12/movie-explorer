from services.search_services import SearchService
from services.favorites_services import add_favorite, list_favorites
from exceptions import APIError, NotFoundError, InvalidResponseError

def print_movie(movie):
    print("\n--- DETTAGLI FILM/SERIE ---")
    print(f"Titolo: {movie['title']}")
    print(f"Anno: {movie['year']}")
    print(f"Tipo: {movie['content_type']}")
    print(f"Genere: {movie['genre']}")
    print(f"Trama: {movie['plot']}")
    print(f"Voto IMDb: {movie['rating']}")
    print(f"Durata: {movie['runtime']}")
    print(f"Attori: {movie['actors']}")
    print(f"Poster: {movie['poster']}")
    print(f"Trailer titolo: {movie['trailer_title']}")
    print(f"Trailer URL: {movie['trailer_url']}")
    print("---------------------------\n")


def print_favorites(favorites):
    print("\n--- PREFERITI ---")
    if not favorites:
        print("nessun preferito salvato")

    else:
        for movie in favorites:
            print(f"- {movie['title']} ({movie['year']})")
    print("-----------------\n")


def main():
    search_service = SearchService()
    while True:
        print("1. Cerca film/serie")
        print("2. Mostra preferiti")
        print("3. Esci")

        choice = input("Scegli un'opzione: ").strip()
        if choice == "1":
            title = input("Inserisci il titolo: ").strip()
            if not title:
                print("titolo vuoto.\n")
                continue

            try:
                movie = search_service.search(title)
                print_movie(movie)
                save_choice = input("Vuoi salvare nei preferiti? (s/n): ").strip().lower()
                if save_choice == "s":
                    add_favorite(movie)
                    print("Salvato nei preferiti.\n")

            except NotFoundError as error:
                print(f"Errore: {error}\n")

            except APIError as error:
                print(f"Errore API: {error}\n")

            except InvalidResponseError as error:
                print(f"Errore risposta: {error}\n")

            except Exception as error:
                raise

        elif choice == "2":
            favorites = list_favorites()
            print_favorites(favorites)

        
        elif choice == "3":
            print("Uscita dal programma")
            break


        else:
            print("scelta non valida")


if __name__ == "__main__":
    main()



