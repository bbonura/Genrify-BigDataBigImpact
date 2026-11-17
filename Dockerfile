# which base image? we want Python 3.12 with little else (the "slim" variant). format is name:tag
FROM ____

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# which file lists the packages to install? it is copied on its own first, so Docker can cache the install step. the ./ means "into /app"
COPY ____ ./
RUN pip install -r requirements.txt

# the container only contains what you COPY. which folder holds app/ and models/? (the destination ./backend matches --app-dir below)
COPY ____ ./backend

RUN useradd --create-home appuser
USER appuser

# which host makes the server reachable from outside the container? (127.0.0.1 would only accept connections from inside it). which port is the fallback? (Render sets $PORT, and the shell expands it here)
CMD ["sh", "-c", "uvicorn app.main:app --app-dir backend --host ____ --port ${PORT:-____}"]
