# QueMe

QueMe is a web application that uses machine learning algorithms to create personalized music playlists based on your preferences. Build, save, and export playlists with just a few clicks.

## Features

- **Smart Playlist Generation**: Build playlists based on artist or genre preferences
- **ML-Powered Recommendations**: Uses scikit-learn for creating data-driven music suggestions
- **Playlist Management**: Save or discard generated playlists
- **Regeneration Options**: Regenerate at the click of a button for alternative suggestions
- **User Dashboard**: Centralized management for all your playlists and account settings
- **External Integrations**: Export saved playlists to Spotify or YouTube Music
- **Secure Authentication**: Login traditionally or use OAuth via Google or GitHub

## Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Machine Learning**: scikit-learn
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with OAuth2
- **Dependency Management**: Poetry and pnpm

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/aileks/QueMe.git
   cd QueMe
   ```

2. Set up environment variables

   ```bash
   cp .env.example .env
   # Edit .env with your configuration values
   ```

3. Install dependencies with Poetry

   ```bash
   poetry install
   ```

4. Initialize the database
   ```bash
   poetry run flask db upgrade
   ```

## Development

1. Start the Flask development server

   ```bash
   poetry run flask run
   ```

2. The server will be available at http://localhost:8000

## Database Migrations

Create and apply database migrations:

```bash
# Generate a migration
poetry run flask db migrate -m "Description of changes"

# Apply migrations
poetry run flask db upgrade
```

## License

[BSD 3-Clause License](LICENSE)
