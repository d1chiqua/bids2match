# Bids2Match

This project is a Python-based web service that processes JSON input to match student topic preferences with available topics. It utilizes Flask to expose an endpoint for topic matching based on user bids and priorities.

## Features
- Accepts JSON payloads containing student-topic preferences.
- Parses and processes data to determine optimal topic assignments.
- Provides a RESTful API endpoint (`/match_topics`).
- Includes unit tests to verify the service's correctness.

## Project Structure
```
project-root/
├── app/                # Application directory
│   ├── app.py          # Main Flask application
│   ├── json_parser.py  # Module for parsing and validating JSON input
│   ├── topics_matcher.py # Module for matching topics based on student bids
│   ├── student.py      # Student class handling proposal acceptance
│   ├── topic.py        # Topic class handling proposal assignments
├── tests/              # Directory for unit tests
│   ├── test_app.py     # Unit tests for the application
├── requirements.txt    # External dependencies
└── README.md           # Documentation file (this file)
```

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

2. **Create a Virtual Environment (Optional but Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
To start the Flask web service locally:
```bash
python app/app.py
```
The service will run in debug mode, typically available at `http://127.0.0.1:5000`.

## API Usage
### Endpoint: `/match_topics`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body Example:**
  ```json
  {
      "tid": [4427, 4428, 4429, 4430],
      "users": {
          "40763": {
              "bids": [
                  { "tid": 4430, "priority": 1, "timestamp": "2025-03-15T17:16:51Z" },
                  { "tid": 4427, "priority": 3, "timestamp": "2025-03-15T17:16:52Z" }
              ],
              "otid": 4429
          }
      },
      "max_accepted_proposals": 3
  }
  ```

- **Response Example:**
  ```json
  {
      "40763": [4430, 4427]
  }
  ```

## Running Tests
To execute unit tests:
```bash
python -m unittest discover
```
This will run all available tests to verify the functionality of the application.

## Deployment
For production, use Gunicorn as a WSGI server:
```bash
gunicorn app.app:app --bind 0.0.0.0:8080
```

## Contributing
If you wish to contribute, please fork the repository, create a feature branch, and submit a pull request.

## License
This project is released under the [MIT License](LICENSE).

