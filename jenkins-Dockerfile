# ------------------------------------------------------------
# Jenkins image for this lab: Jenkins LTS + Docker CLI + Python 3
# Jenkins controls the HOST Docker through /var/run/docker.sock
# (see jenkins/docker-compose.yml). For local study use only.
# ------------------------------------------------------------
FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg python3 \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
       > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli docker-buildx-plugin docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Plugins needed for the lab (Pipeline, Git, GitHub, Stage View)
RUN jenkins-plugin-cli --plugins workflow-aggregator git github pipeline-stage-view

USER jenkins
