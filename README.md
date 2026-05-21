# Network+ & Security+ Certification Exam Web Application

A Python web application built with Flask that provides a comprehensive exam for Network+ and Security+ cybersecurity certification preparation. Test your knowledge with randomly selected questions and get instant feedback with pass/fail results.

## Features

- 📚 **Comprehensive Coverage**: 150 exam questions covering Network+ and Security+ topics
- 🎲 **Randomized Exams**: Each exam randomly selects 20 questions for variety
- ✅ **Instant Feedback**: Get immediate results with detailed answer review
- 📊 **Scoring System**: Pass/fail based on 70% threshold
- 🎨 **Modern UI**: Beautiful, responsive design with gradient styling
- 🔒 **Session-Based**: Secure exam sessions with Flask sessions

## Installation

You can run the application in one of three ways:

1. [Docker Compose / Portainer](#docker-deployment-recommended) (recommended for any deployment)
2. [Plain Docker](#plain-docker)
3. [Local Python](#local-python-development)

---

## Docker Deployment (Recommended)

### Prerequisites

- Docker Engine 20.10+ (and Docker Compose v2), or [Portainer](https://www.portainer.io/) connected to a Docker host

### Quick start (Docker Compose)

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd CNA
   ```

2. Generate a strong secret key and put it in a `.env` file next to `docker-compose.yml`:
   ```bash
   echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env
   ```

3. Build and start the stack:
   ```bash
   docker compose up -d --build
   ```

4. Open <http://localhost:5000>.

To stop the stack: `docker compose down` (data in the `cna-data` volume is preserved).
To wipe data as well: `docker compose down -v`.

### Deploying on Portainer.io

1. Push this repository to a git remote your Portainer instance can reach (or use the **Web editor** option and paste the contents of `docker-compose.yml`).
2. In Portainer: **Stacks → Add stack**.
3. Pick **Repository** and point at your fork (or **Web editor** and paste the compose file).
4. Under **Environment variables**, add:
   - `SECRET_KEY` — a strong random string (`python -c "import secrets; print(secrets.token_hex(32))"`)
5. Click **Deploy the stack**. The app is reachable on port `5000` of the Docker host.

The stack defines a named volume `cna-data` that persists the leaderboard and session files across container recreations.

### Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | hardcoded dev value | Flask session signing key. **Always override in production.** |
| `DATA_DIR` | `/app/data` (in container) | Base directory for mutable state |
| `LEADERBOARD_FILE` | `$DATA_DIR/leaderboard.json` | Leaderboard storage path |
| `SESSION_FILE_DIR` | `$DATA_DIR/flask_session` | Flask-Session storage path |

### Plain Docker

If you'd rather skip Compose:

```bash
docker build -t cna-exam:latest .
docker volume create cna-data
docker run -d \
  --name cna-exam \
  -p 5000:5000 \
  -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
  -v cna-data:/app/data \
  --restart unless-stopped \
  cna-exam:latest
```

---

## Local Python (Development)

### Prerequisites

- Python 3.10 or higher (tested on 3.12)
- pip

### Setup

1. (Optional but recommended) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # on Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Flask dev server:
   ```bash
   python app.py
   ```

4. Open <http://localhost:5000> and click **Start Exam**.

> The dev server (`app.run`) is single-threaded and is **not** suitable for production. The Docker image uses Gunicorn instead.

## How It Works

1. **Start Page**: View exam information and requirements
2. **Exam Page**: Answer 20 randomly selected questions from 150 available
3. **Results Page**: See your score, pass/fail status, and detailed review of all answers

## Exam Details

- **Total Questions Pool**: 150 questions
- **Questions Per Exam**: 20 randomly selected
- **Passing Score**: 70%
- **Topics Covered**: 
  - Network protocols and ports
  - Network security concepts
  - Encryption and authentication
  - OSI model and networking fundamentals
  - Cybersecurity threats and defenses
  - Wireless security (802.11 standards, WEP/WPA/WPA2/WPA3)
  - Network troubleshooting
  - Routing and switching (RIP, OSPF, BGP, EIGRP)
  - Network access control (NAC, 802.1X)
  - VPN and remote access
  - Security frameworks (CIA, RBAC, NIST)
  - Physical and logical security
  - Malware types and attacks
  - Compliance and regulations (GDPR, SOX, HIPAA)
  - Industrial control systems (SCADA, ICS)
  - IPv6 addressing and transition technologies

## Security Note

**Important**: Always override the secret key in production by setting the `SECRET_KEY` environment variable. The hardcoded fallback in `app.py` is for local development only.

Generate one with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

For Docker / Portainer deployments, set `SECRET_KEY` in the stack's environment variables (see [Docker Deployment](#docker-deployment-recommended)). For local runs, you can export it before starting:
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python app.py
```

## Customization

### Adding More Questions

Edit the `QUESTIONS` list in `app.py` to add more exam questions:

```python
{
    "id": 26,
    "question": "Your question here?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "correct": 0,  # Index of correct answer (0-3)
    "topic": "Network+"
}
```

### Changing Exam Size

Modify the `EXAM_SIZE` variable in `app.py`:

```python
EXAM_SIZE = 20  # Change to desired number of questions
```

### Adjusting Pass Score

Change the passing threshold in the `results` function in `app.py`:

```python
passed = score >= 80  # Change 70 to desired percentage
```

## Project Structure

```
CNA/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (Flask, Flask-Session, Gunicorn)
├── Dockerfile             # Container image (Python 3.12-slim + Gunicorn)
├── docker-compose.yml     # Portainer / Docker Compose stack definition
├── .dockerignore          # Build-context exclusions
├── README.md              # This file
├── leaderboard.json       # Local-dev leaderboard store (Docker uses a volume)
├── templates/             # HTML templates
│   ├── index.html         # Welcome/start page
│   ├── exam.html          # Exam interface
│   ├── results.html       # Results page
│   └── leaderboard.html   # Leaderboard view
└── static/                # Static assets (CSS, etc.)
```

## Technologies Used

- **Flask 3** — web framework
- **Flask-Session** — server-side filesystem sessions
- **Gunicorn** — production WSGI server (used in the Docker image)
- **Python 3.12** — runtime in the container
- **Docker / Docker Compose** — packaging and deployment
- **HTML / CSS** — frontend

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to add more questions, improve the UI, or enhance functionality!

## Support

For issues or questions, please create an issue in the repository.

