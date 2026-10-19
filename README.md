# srazh-aidyn-devops

**Laboratory work 1 — DevOps Fundamentals: Linux, Git, Docker and Jenkins**

| | |
|---|---|
| **Student** | Srazh Aidyn |
| **Group** | IT2-2308 (4th year) |
| **Student ID** | 36210 |
| **Course** | DevOps |

A personalized DevOps project that goes through the whole chain
**Linux → Git → GitHub → Docker → Jenkins**. The application is a small Python web service
that prints the student information to the console and shows it on a web page.

## Naming convention

| Element | Name |
|---|---|
| Linux directory | `~/devops/srazh_aidyn/` |
| Bash script | `scripts/Srazh_Aidyn_system.sh` |
| GitHub repository | `srazh-aidyn-devops` |
| Docker image | `srazh-aidyn-devops` |
| Docker container | `srazh-aidyn-container` |
| Jenkins Job | `Srazh_Aidyn_DevOps` |

## Project structure

```
srazh_aidyn/
├── Srazh_Aidyn_info.txt        # student information
├── app/
│   ├── app.py                  # Python application (HTTP server, port 8085)
│   └── test_app.py             # unit tests (Jenkins Test stage, Docker RUN)
├── scripts/
│   ├── Srazh_Aidyn_system.sh   # student + system information
│   ├── check_project.sh        # structure checks (Jenkins Test stage)
│   └── set_student_id.sh       # replaces the Student ID placeholder
├── config/app.conf             # application configuration (KEY=VALUE)
├── logs/                       # application.log — ignored by Git
├── backup/                     # ignored by Git
├── private.txt                 # chmod 600  (rw-------)
├── public.txt                  # chmod 644  (rw-r--r--)
├── Dockerfile
├── docker-compose.yml
├── Jenkinsfile                 # Checkout → Build → Test → Docker Build → Docker Run
├── jenkins/                    # local Jenkins (LTS + Docker CLI) for the lab
├── .gitignore  .dockerignore  .env.example
└── README.md
```

## Quick start

```bash
# Bash script
chmod +x scripts/Srazh_Aidyn_system.sh
./scripts/Srazh_Aidyn_system.sh

# Docker
docker build -t srazh-aidyn-devops .
docker run -d --name srazh-aidyn-container -p 8085:8085 \
  -e STUDENT_NAME=Aidyn -e STUDENT_SURNAME=Srazh \
  -e STUDENT_GROUP=IT2-2308 -e STUDENT_ID=36210 \
  srazh-aidyn-devops
docker logs srazh-aidyn-container
curl http://localhost:8085/health          # {"status": "ok", ...}
# open http://localhost:8085 in a browser

# Docker Compose (port 8086)
docker compose up -d --build
docker compose ps
docker compose down

# Tests
python3 -m unittest discover -s app -p "test_*.py" -v
./scripts/check_project.sh
```

## Application endpoints

| URL | Response |
|---|---|
| `/` | HTML page with student information |
| `/health` | `{"status": "ok"}` — used by Docker HEALTHCHECK and Jenkins |
| `/info` | student information as JSON |

Configuration priority: **environment variables → `config/app.conf` → defaults in code**.

## Jenkins

```bash
cd jenkins && docker compose up -d --build      # Jenkins on http://localhost:8080
docker exec srazh-aidyn-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Job **Srazh_Aidyn_DevOps** → *Pipeline* → *Pipeline script from SCM* → Git →
`https://github.com/<username>/srazh-aidyn-devops.git`, branch `*/main`, script path `Jenkinsfile`.

Pipeline stages: **Checkout → Build → Test → Docker Build → Docker Run** → `Finished: SUCCESS`.
