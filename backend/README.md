# Gemini-Explainer Web System

A professional web-based system that explains PowerPoint presentations using Google's Gemini AI. This system transforms the original script-based Gemini-Explainer into a distributed web application with multiple components and professional database management.

## Branch Structure

The project is organized into a feature branch that contains all components:

**`Feat/solution-part3`** - Contains the complete web system implementation:
- Web API with Flask
- Explainer Service
- Python Client Library
- SQLite Database with SQLAlchemy ORM
- Shared directory structure
- Test scripts

## Project Structure

```
gemini-explainer-web/
│
├── gemini-explainer/          # Original project files
│   ├── ppt_parser.py          # PowerPoint parsing functions
│   ├── gemini_client.py       # Gemini API interaction
│   ├── main.py                # Main script
│   ├── test_script.py         # System tests
│   └── .env                   # Environment variables with API key
│
├── database.py                # SQLAlchemy ORM models & DB connection
├── init_db.py                 # Database initialization script
│
├── db/                        # Database directory (auto-created)
│   └── gemini_explainer.db    # SQLite database file
│
├── api/                       # Web API component
│   ├── app.py                 # Flask application with database integration
│   └── requirements.txt       # Dependencies
│
├── explainer/                 # Explainer service
│   ├── explainer_service.py   # Database-driven processing service
│   └── requirements.txt       # Dependencies
│
├── client/                    # Python client
│   ├── src/
│   │   └── gemini_explainer_client/
│   │       ├── __init__.py
│   │       └── client.py      # Enhanced client with email support
│   └── pyproject.toml         # Package configuration
│
├── shared/                    # Shared data directories (created automatically)
│   ├── uploads/               # Uploaded files (stored as {uid}.pptx)
│   ├── outputs/               # Processed results (stored as {uid}.json)
│   └── logs/                  # Log files
│       ├── api/               # API logs
│       └── explainer/         # Explainer logs
│
├── tests/                     # System tests
│   └── test_system.py         # End-to-end tests with database
│
└── README.md                  # Project documentation
```

## System Architecture

The system consists of four main components:

### 1. **Database Layer (SQLite + SQLAlchemy)**
- **Users Table**: Stores user information (email-based)
- **Uploads Table**: Tracks all file uploads with metadata
- **Status Tracking**: `uploaded` → `processing` → `completed`/`failed`
- **Error Logging**: Database-stored error messages

### 2. **Web API (Flask)**
- Handles client requests with database integration
- Supports anonymous uploads and user-associated uploads
- Status queries by UID or email/filename combination
- Email validation with professional error handling

### 3. **Explainer Service**
- Database-driven file discovery (no filesystem scanning)
- Real-time status updates in database
- Enhanced error handling and logging
- Automatic status progression and finish time tracking

### 4. **Python Client**
- Convenient interface with email support
- Multiple status query methods
- Upload history retrieval
- Enhanced error handling

## Database Schema

### Users Table
- `id` (Primary Key, Auto-increment)
- `email` (Unique, Not Null)

### Uploads Table
- `id` (Primary Key, Auto-increment)
- `uid` (Unique UUID)
- `filename` (Original filename)
- `upload_time` (Upload timestamp)
- `finish_time` (Processing completion time)
- `status` (`uploaded`, `processing`, `completed`, `failed`)
- `error_message` (Error details for failed uploads)
- `user_id` (Foreign Key to Users, nullable for anonymous uploads)

## Installation

### Prerequisites
- Python 3.8+
- PowerPoint presentation files (.pptx)
- Google Gemini API key

### Steps

1. **Initialize the database**:
   ```bash
   python init_db.py
   ```

2. **Install the API dependencies**:
   ```bash
   cd api
   pip install -r requirements.txt
   ```

3. **Install the Explainer dependencies**:
   ```bash
   cd explainer
   pip install -r requirements.txt
   ```

4. **Install the Python client (development mode)**:
   ```bash
   cd client
   pip install -e .
   ```

5. **Ensure your `.env` file in the `gemini-explainer` directory contains your Gemini API key**:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Running the System

1. **Start the Web API** (in one terminal):
   ```bash
   cd api
   python app.py
   ```

2. **Start the Explainer service** (in another terminal):
   ```bash
   cd explainer
   python explainer_service.py
   ```

## Usage

### Using the Python Client

#### Anonymous Upload
```python
from gemini_explainer_client import ExplainerClient

# Initialize the client
client = ExplainerClient()

# Upload a presentation anonymously
uid = client.upload("path/to/presentation.pptx")
print(f"Uploaded with UID: {uid}")

# Check status by UID
status = client.status(uid)
if status.is_pending():
    print("Still processing...")
elif status.is_done():
    print(f"Processing complete! Found {len(status.explanation)} slides")
elif status.is_failed():
    print(f"Processing failed: {status.error_message}")
```

#### Upload with User Email
```python
# Upload with email association
uid = client.upload("path/to/presentation.pptx", email="user@example.com")

# Check status by email and filename
status = client.status_by_email_filename("user@example.com", "presentation.pptx")
print(f"Latest upload status: {status.status}")

# Get upload history for user
history = client.history("user@example.com")
print(f"Total uploads: {history['total_uploads']}")
for upload in history['uploads']:
    print(f"- {upload['filename']}: {upload['status']}")
```

## Testing

### Running the Automated Test

The project includes a comprehensive end-to-end test with database integration:

```bash
cd tests
python test_system.py
```


## Database Management

### Initialize/Reset Database:
```bash
python init_db.py --force  # Recreates database (deletes existing data)
```

### View Database Contents:
- **PyCharm Professional**: Use Database Tool Window
- **VSCode**: Install SQLite extension
- **Third-party**: Use [SQLite Browser](https://sqlitebrowser.org/)

### Database Location:
The SQLite database file is located at: `db/gemini_explainer.db`