# Ronin's Vocab - 11+ Exam Practice Tool

A modern vocabulary practice tool built with FastHTML and Claude AI, designed to help students prepare for the 11+ exam.

## Features

- **Multiple Choice Quiz**: Practice vocabulary with AI-generated challenging options
- **Word Management**: Add and remove words from your practice list
- **Progress Tracking**: Monitor your streak and overall progress
- **Modern UI**: Clean, Notion-inspired design
- **Persistent Storage**: Words are saved in a database

## Setup

1. Clone the repository
2. Copy `.env.template` to `.env` and add your Anthropic API key:
   ```
   cp .env.template .env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:
   ```bash
   python main.py
   ```

## Deployment to Vercel

1. Push your code to GitHub

2. Go to [Vercel](https://vercel.com) and import your GitHub repository

3. Add your environment variable in Vercel:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key

4. Deploy! Vercel will automatically detect FastHTML and configure the deployment

## Database

- Local development uses SQLite
- Production on Vercel can use Vercel Postgres (automatically configured)
- The app comes pre-loaded with 45 common 11+ vocabulary words

## Tech Stack

- **FastHTML**: Modern Python web framework
- **Claude AI**: For generating quiz options
- **SQLAlchemy**: Database ORM
- **Vercel**: Deployment platform