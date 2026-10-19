# ------------------------------------------------------------
# Dockerfile — srazh-aidyn-devops
# Build:  docker build -t srazh-aidyn-devops .
# Run:    docker run --name srazh-aidyn-container -p 8085:8085 srazh-aidyn-devops
# ------------------------------------------------------------

# FROM — base image: official slim Python 3.12 (Debian based)
FROM python:3.12-slim

# Build arguments (passed by Jenkins: --build-arg GIT_COMMIT=... --build-arg BUILD_NUMBER=...)
ARG GIT_COMMIT=local
ARG BUILD_NUMBER=manual

# Metadata of the image (visible in `docker inspect`)
LABEL maintainer="Srazh Aidyn <IT2-2308>" \
      project="srazh-aidyn-devops" \
      course="DevOps" \
      git_commit="${GIT_COMMIT}"

# Environment inside the container (non-sensitive values only!)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_PORT=8085 \
    GIT_COMMIT=${GIT_COMMIT} \
    BUILD_NUMBER=${BUILD_NUMBER}

# WORKDIR — working directory; all next commands run inside /app
WORKDIR /app

# COPY — copy project files from the build context into the image
COPY app/app.py app/test_app.py ./
COPY config/app.conf ./config/app.conf
COPY Srazh_Aidyn_info.txt ./

# RUN — executed once at BUILD time: create a non-root user and give it the files,
# then run the unit tests so a broken application never becomes an image
RUN useradd --no-create-home --uid 1001 --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app \
    && python3 -m unittest -q test_app

# Run the application as a normal user, not as root (security best practice)
USER appuser

# EXPOSE — documents the port the application listens on
EXPOSE 8085

# Docker checks the /health endpoint every 30 s -> status "healthy" in `docker ps`
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8085/health', timeout=2)" || exit 1

# CMD — default command executed when the CONTAINER starts
CMD ["python3", "app.py"]
