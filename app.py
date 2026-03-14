from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from config import BASE_URL, FLASK_SECRET_KEY
from database import init_db
from exceptions import APIError, InvalidResponseError, NotFoundError
from services.user_favorites_service import add_favorite_for_user, list_favorites_for_user, remove_favorite_for_user
from services.search_services import SearchService
from services.account_service import delete_user_account, get_recent_searches, save_recent_search
from services.account_security_service import delete_otp, generate_otp, get_valid_otp, is_otp_expired, save_otp
from services.email_service import send_otp_email, send_reset_email
from services.auth_service import (
    create_user,
    get_user_by_email,
    get_user_by_reset_token,
    is_reset_token_expired,
    is_valid_email,
    save_reset_token,
    update_user_password,
    user_exists,
    validate_password,
    verify_user_login
)
from services.external_video_service import (
    build_movie_video_url,
    build_tv_video_url,
    get_provider_origin
)
from services.history_service import (
    create_or_get_watch_record,
    update_watch_progress,
    mark_watch_completed,
    get_continue_watching
)
import secrets
import datetime

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

init_db()
search_service = SearchService()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not first_name or not last_name or not email or not username or not password:
            flash("Compila tutti i campi richiesti.")
            return redirect(url_for("register"))

        if not is_valid_email(email):
            flash("Inserisci un'email valida.")
            return redirect(url_for("register"))

        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for("register"))

        existing_user = user_exists(email, username)
        if existing_user:
            flash("Email o nome utente già registrati.")
            return redirect(url_for("register"))

        create_user(first_name, last_name, email, username, password)

        flash("Registrazione completata con successo. Ora puoi fare login.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not identifier or not password:
            flash("Inserisci nome utente o email e password.")
            return redirect(url_for("login"))

        user = verify_user_login(identifier, password)

        if user is None:
            flash("Credenziali non valide.")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["first_name"] = user["first_name"]
        session["last_name"] = user["last_name"]
        session["email"] = user["email"]

        flash("Login effettuato con successo.")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logout effettuato con successo.")
    return redirect(url_for("home"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Inserisci la tua email.")
            return redirect(url_for("forgot_password"))

        user = get_user_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)
            expiry = (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()

            save_reset_token(user["id"], token, expiry)

            reset_link = f"{BASE_URL}/reset-password/{token}"

            try:
                send_reset_email(email, reset_link)
            except Exception:
                flash("Errore durante l'invio dell'email. Controlla la configurazione SMTP.")
                return redirect(url_for("forgot_password"))

        flash("Se l'email esiste nel sistema, riceverai un link per reimpostare la password.")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = get_user_by_reset_token(token)

    if not user:
        flash("Token di reset non valido.")
        return redirect(url_for("login"))

    if is_reset_token_expired(user["reset_token_expiry"]):
        flash("Il link di reset è scaduto.")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if not password:
            flash("Inserisci una nuova password.")
            return redirect(url_for("reset_password", token=token))

        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for("reset_password", token=token))

        update_user_password(user["id"], password)

        flash("Password aggiornata con successo. Ora puoi fare login.")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.route("/account")
def account():
    if not session.get("user_id"):
        flash("Devi effettuare il login per accedere al tuo account.")
        return redirect(url_for("login"))

    recent_searches = get_recent_searches(session["user_id"])
    return render_template("account.html", recent_searches=recent_searches)


@app.route("/account/request-password-otp", methods=["POST"])
def request_password_otp():
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    otp_code = generate_otp()
    save_otp(session["user_id"], otp_code, "change_password")

    try:
        send_otp_email(session["email"], otp_code, "change_password")
    except Exception as error:
        flash(f"Errore invio email OTP: {error}")
        return redirect(url_for("account"))

    flash("Ti abbiamo inviato un codice OTP via email.")
    return redirect(url_for("verify_password_otp"))


@app.route("/account/verify-password-otp", methods=["GET", "POST"])
def verify_password_otp():
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    if request.method == "POST":
        otp_code = request.form.get("otp_code", "").strip()

        if not otp_code:
            flash("Inserisci il codice OTP.")
            return redirect(url_for("verify_password_otp"))

        otp_row = get_valid_otp(session["user_id"], otp_code, "change_password")

        if not otp_row:
            flash("Codice OTP non valido.")
            return redirect(url_for("verify_password_otp"))

        if is_otp_expired(otp_row["expires_at"]):
            delete_otp(session["user_id"], "change_password")
            flash("Codice OTP scaduto.")
            return redirect(url_for("account"))

        session["password_otp_verified"] = True
        flash("OTP verificato. Ora puoi impostare una nuova password.")
        return redirect(url_for("change_password_with_otp"))

    return render_template("verify_password_otp.html")


@app.route("/account/change-password", methods=["GET", "POST"])
def change_password_with_otp():
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    if not session.get("password_otp_verified"):
        flash("Devi prima verificare il codice OTP.")
        return redirect(url_for("account"))

    if request.method == "POST":
        password = request.form.get("password", "").strip()

        if not password:
            flash("Inserisci una nuova password.")
            return redirect(url_for("change_password_with_otp"))

        password_error = validate_password(password)
        if password_error:
            flash(password_error)
            return redirect(url_for("change_password_with_otp"))

        update_user_password(session["user_id"], password)
        delete_otp(session["user_id"], "change_password")
        session.pop("password_otp_verified", None)

        flash("Password aggiornata con successo.")
        return redirect(url_for("account"))

    return render_template("change_password_otp.html")


@app.route("/account/request-delete-otp", methods=["POST"])
def request_delete_otp():
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    otp_code = generate_otp()
    save_otp(session["user_id"], otp_code, "delete_account")

    try:
        send_otp_email(session["email"], otp_code, "delete_account")
    except Exception as error:
        flash(f"Errore invio email OTP: {error}")
        return redirect(url_for("account"))

    flash("Ti abbiamo inviato un codice OTP per confermare l'eliminazione account.")
    return redirect(url_for("verify_delete_otp"))


@app.route("/account/verify-delete-otp", methods=["GET", "POST"])
def verify_delete_otp():
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    if request.method == "POST":
        otp_code = request.form.get("otp_code", "").strip()

        if not otp_code:
            flash("Inserisci il codice OTP.")
            return redirect(url_for("verify_delete_otp"))

        otp_row = get_valid_otp(session["user_id"], otp_code, "delete_account")

        if not otp_row:
            flash("Codice OTP non valido.")
            return redirect(url_for("verify_delete_otp"))

        if is_otp_expired(otp_row["expires_at"]):
            delete_otp(session["user_id"], "delete_account")
            flash("Codice OTP scaduto.")
            return redirect(url_for("account"))

        delete_user_account(session["user_id"])
        session.clear()

        flash("Il tuo account è stato eliminato con successo.")
        return redirect(url_for("home"))

    return render_template("verify_delete_otp.html")


@app.route("/player/movie/<int:movie_id>")
def player_movie(movie_id):
    if "user_id" not in session:
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    try:
        movie = search_service.search_movie(movie_id)

        record = create_or_get_watch_record(
            session["user_id"],
            movie_id,
            movie["title"],
            movie["poster"],
            content_type="movie"
        )

        start_at = record["progress_seconds"] if record else 0
        player_url = build_movie_video_url(movie_id, start_at=start_at)

        return render_template(
            "player_movie.html",
            movie=movie,
            movie_id=movie_id,
            player_url=player_url,
            provider_origin=get_provider_origin(),
            is_tv=False,
            season=None,
            episode=None
        )

    except Exception as error:
        flash(f"Errore apertura player film: {error}")
        return redirect(url_for("home"))


@app.route("/player/tv/<int:tv_id>/<int:season>/<int:episode>")
def player_tv(tv_id, season, episode):
    if "user_id" not in session:
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    try:
        tv_show = search_service.search_tv(tv_id)

        title = f"{tv_show['title']} - S{season}E{episode}"

        record = create_or_get_watch_record(
            session["user_id"],
            tv_id,
            title,
            tv_show["poster"],
            content_type="tv",
            season=season,
            episode=episode
        )

        start_at = record["progress_seconds"] if record else 0
        player_url = build_tv_video_url(tv_id, season, episode, start_at=start_at)

        return render_template(
            "player_movie.html",
            movie={"title": title},
            movie_id=tv_id,
            player_url=player_url,
            provider_origin=get_provider_origin(),
            is_tv=True,
            season=season,
            episode=episode
        )

    except Exception as error:
        flash(f"Errore apertura player serie: {error}")
        return redirect(url_for("home"))


@app.route("/watch/movie/<int:movie_id>")
def watch_movie(movie_id):
    if "user_id" not in session:
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    return redirect(url_for("player_movie", movie_id=movie_id))


@app.route("/watch/tv/<int:tv_id>/<int:season>/<int:episode>")
def watch_tv(tv_id, season, episode):
    if "user_id" not in session:
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    return redirect(url_for("player_tv", tv_id=tv_id, season=season, episode=episode))


@app.route("/api/watch-complete", methods=["POST"])
def save_watch_complete():
    if "user_id" not in session:
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    try:
        tmdb_id = int(data.get("tmdb_id"))
        content_type = data.get("content_type", "movie")
        season = data.get("season")
        episode = data.get("episode")

        if season is not None:
            season = int(season)
        if episode is not None:
            episode = int(episode)

        mark_watch_completed(
            session["user_id"],
            tmdb_id,
            content_type=content_type,
            season=season,
            episode=episode
        )

        return jsonify({"ok": True})

    except Exception as error:
        return jsonify({"ok": False, "error": str(error)}), 400


@app.route("/api/watch-progress", methods=["POST"])
def watch_progress():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "error": "not logged"}), 401

        data = request.get_json(silent=True) or {}

        user_id = session["user_id"]
        tmdb_id = int(data.get("tmdb_id"))
        event_name = data.get("event")
        progress_seconds = int(float(data.get("progress_seconds", 0)))
        duration_seconds = int(float(data.get("duration_seconds", 0)))
        content_type = data.get("content_type", "movie")
        season = data.get("season")
        episode = data.get("episode")

        if season is not None:
            season = int(season)
        if episode is not None:
            episode = int(episode)

        # assicura che il record esista sempre
        if content_type == "tv":
            tv_show = search_service.search_tv(tmdb_id)
            title = f"{tv_show['title']} - S{season}E{episode}"
            poster_path = tv_show["poster"]
        else:
            movie = search_service.search_movie(tmdb_id)
            title = movie["title"]
            poster_path = movie["poster"]

        create_or_get_watch_record(
            user_id,
            tmdb_id,
            title,
            poster_path,
            content_type=content_type,
            season=season,
            episode=episode
        )

        update_watch_progress(
            user_id,
            tmdb_id,
            progress_seconds,
            duration_seconds,
            content_type=content_type,
            season=season,
            episode=episode
        )

        if event_name == "ended":
            mark_watch_completed(
                user_id,
                tmdb_id,
                content_type=content_type,
                season=season,
                episode=episode
            )

        return jsonify({"success": True})

    except Exception as error:
        print("ERRORE watch-progress:", repr(error))
        return jsonify({"success": False, "error": str(error)}), 500


@app.route("/accept-cookies", methods=["POST"])
def accept_cookies():
    response = redirect(request.referrer or url_for("home"))
    response.set_cookie(
        "cookie_consent",
        "accepted",
        max_age=60 * 60 * 24 * 180,
        samesite="Lax"
    )
    flash("Preferenze cookie salvate.")
    return response


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/")
def home():
    featured_items = search_service.get_featured_content()

    if not isinstance(featured_items, list):
        featured_items = []

    # ottimizzazione: trailer solo per i primi 2 film in hero
    for index, item in enumerate(featured_items):
        if isinstance(item, dict) and "id" in item:
            item["watch_url"] = build_movie_video_url(item["id"])
            item["year"] = (item.get("release_date") or "")[:4]
            item["rating"] = item.get("vote_average", "")
            item["trailer_url"] = ""

            if index < 2:
                try:
                    movie_details = search_service.tmdb_client.get_movie_details(item["id"])
                    trailer_data = search_service.tmdb_client.get_trailer_data(movie_details)

                    if trailer_data and trailer_data.get("video_id"):
                        item["trailer_url"] = (
                            f"https://www.youtube.com/embed/{trailer_data['video_id']}"
                            "?autoplay=1&mute=1&controls=0&modestbranding=1&rel=0&playsinline=1&disablekb=1&fs=0"
                        )
                except Exception:
                    item["trailer_url"] = ""

    now_playing_movies = search_service.get_now_playing_movies()
    top_rated_movies = search_service.get_top_rated_movies()
    popular_movies = search_service.get_popular_movies()
    popular_tv = search_service.get_popular_tv()

    continue_watching = []
    if "user_id" in session:
        try:
            continue_watching = get_continue_watching(session["user_id"], limit=5)
        except Exception as error:
            print("Errore continue_watching:", error)
            continue_watching = []

    return render_template(
        "home.html",
        continue_watching=continue_watching,
        featured_items=featured_items,
        now_playing_movies=now_playing_movies,
        top_rated_movies=top_rated_movies,
        popular_movies=popular_movies,
        popular_tv=popular_tv
    )


@app.route("/search", methods=["POST"])
def search():
    title = request.form.get("title", "").strip()

    if not title:
        flash("Inserisci un titolo prima di cercare.")
        return redirect(url_for("home"))

    if session.get("user_id"):
        save_recent_search(session["user_id"], title)

    try:
        results = search_service.search_many(title)

        if len(results) == 1:
            item = results[0]

            if item["media_type"] == "movie":
                return redirect(url_for("movie_detail", movie_id=item["id"]))

            if item["media_type"] == "tv":
                return redirect(url_for("tv_detail", tv_id=item["id"]))

        return render_template("search_results.html", results=results, query=title)

    except NotFoundError as error:
        flash(str(error))
        return redirect(url_for("home"))

    except APIError as error:
        flash(f"Errore API: {error}")
        return redirect(url_for("home"))

    except InvalidResponseError as error:
        flash(f"Risposta non valida: {error}")
        return redirect(url_for("home"))

    except Exception as error:
        flash(f"Errore imprevisto: {error}")
        return redirect(url_for("home"))


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    try:
        movie = search_service.search_movie(movie_id)
        recommendations = search_service.get_movie_recommendations(movie_id)
        watch_providers = search_service.get_movie_watch_providers(movie_id)
        video_url = build_movie_video_url(movie_id)

        return render_template(
            "result.html",
            movie=movie,
            recommendations=recommendations,
            watch_providers=watch_providers,
            video_url=video_url,
            is_tv=False,
            seasons=[],
            episodes=[],
            selected_season=None,
            selected_episode=None
        )

    except NotFoundError as error:
        flash(str(error))
        return redirect(url_for("home"))

    except APIError as error:
        flash(f"Errore API: {error}")
        return redirect(url_for("home"))

    except InvalidResponseError as error:
        flash(f"Risposta non valida: {error}")
        return redirect(url_for("home"))

    except Exception as error:
        flash(f"Errore imprevisto: {error}")
        return redirect(url_for("home"))


@app.route("/tv/<int:tv_id>")
def tv_detail(tv_id):
    try:
        movie = search_service.search_tv(tv_id)
        recommendations = search_service.get_tv_recommendations(tv_id)
        watch_providers = search_service.get_tv_watch_providers(tv_id)

        tv_data = search_service.tmdb_client.get_tv_details(tv_id)
        seasons = tv_data.get("seasons", [])

        valid_seasons = [season for season in seasons if season.get("season_number", 0) > 0]

        selected_season = request.args.get("season")
        if not selected_season:
            if valid_seasons:
                selected_season = str(valid_seasons[0]["season_number"])
            else:
                selected_season = "1"

        season_data = search_service.get_tv_season_details(tv_id, selected_season)
        episodes = season_data.get("episodes", [])

        selected_episode = request.args.get("episode")
        valid_episode_numbers = [str(ep.get("episode_number")) for ep in episodes if ep.get("episode_number")]

        if not selected_episode or selected_episode not in valid_episode_numbers:
            selected_episode = valid_episode_numbers[0] if valid_episode_numbers else "1"

        return render_template(
            "result.html",
            movie=movie,
            recommendations=recommendations,
            watch_providers=watch_providers,
            is_tv=True,
            seasons=valid_seasons,
            episodes=episodes,
            selected_season=selected_season,
            selected_episode=selected_episode
        )

    except NotFoundError as error:
        flash(str(error))
        return redirect(url_for("home"))

    except APIError as error:
        flash(f"Errore API: {error}")
        return redirect(url_for("home"))

    except InvalidResponseError as error:
        flash(f"Risposta non valida: {error}")
        return redirect(url_for("home"))

    except Exception as error:
        flash(f"Errore imprevisto: {error}")
        return redirect(url_for("home"))


@app.route("/favorites")
def favorites():
    if not session.get("user_id"):
        flash("Devi effettuare il login per vedere i preferiti.")
        return redirect(url_for("login"))

    favorites_list = list_favorites_for_user(session["user_id"])
    return render_template("favorites.html", favorites=favorites_list)


@app.route("/favorites/add", methods=["POST"])
def add_to_favorites():
    if not session.get("user_id"):
        flash("Devi effettuare il login per aggiungere preferiti.")
        return redirect(url_for("login"))

    movie_data = {
        "title": request.form.get("title", ""),
        "year": request.form.get("year", ""),
        "imdb_id": request.form.get("imdb_id", ""),
        "content_type": request.form.get("content_type", ""),
        "genre": request.form.get("genre", ""),
        "plot": request.form.get("plot", ""),
        "rating": request.form.get("rating", ""),
        "runtime": request.form.get("runtime", ""),
        "actors": request.form.get("actors", ""),
        "poster": request.form.get("poster", ""),
        "trailer_title": request.form.get("trailer_title", ""),
        "trailer_url": request.form.get("trailer_url", ""),
        "trailer_video_id": request.form.get("trailer_video_id", "")
    }

    added = add_favorite_for_user(session["user_id"], movie_data)

    if added:
        flash("Film aggiunto ai tuoi preferiti.")
    else:
        flash("Questo film è già nei tuoi preferiti.")

    return redirect(url_for("favorites"))


@app.route("/favorites/remove/<imdb_id>", methods=["POST"])
def remove_from_favorites(imdb_id):
    if not session.get("user_id"):
        flash("Devi effettuare il login.")
        return redirect(url_for("login"))

    remove_favorite_for_user(session["user_id"], imdb_id)
    flash("Film rimosso dai tuoi preferiti.")
    return redirect(url_for("favorites"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,)