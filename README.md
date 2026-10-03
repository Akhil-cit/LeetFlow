# LeetCode Daily AI Agent

An AI agent that automatically handles the LeetCode Daily Challenge once every day, running entirely in the cloud via GitHub Actions.

*Note: This project is currently in Phase 1 of development.*

## Features (Planned)
- Fully automated daily execution on GitHub Actions (Zero cost).
- Solves LeetCode Daily Challenges using AI.
- Code testing and AI-driven debugging loop.
- No local setup required for daily runs.

## Architecture
GitHub Repository -> GitHub Actions Scheduler -> Cloud Runner -> Python AI Agent -> Playwright -> LeetCode -> AI Solver -> Result

## Local Setup (For Development)

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate it and install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your credentials.
5. Run the agent: `python -m agent.main`

## GitHub Setup (For Cloud Execution)

1. Fork or clone this repository to your GitHub account.
2. Go to your repository settings -> Secrets and variables -> Actions.
3. Add the following repository secrets:
   - `LEETCODE_USERNAME`
   - `LEETCODE_PASSWORD`
   - `AI_API_KEY`
4. The agent will run automatically based on the schedule in `.github/workflows/daily.yml`.
5. You can also trigger it manually from the "Actions" tab by clicking "Run workflow".
