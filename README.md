# CCR Management System

A web-based reservation and management system built with Flask, featuring user authentication, video processing, and real-time scheduling capabilities.

## Features

- User Authentication (Login/Register)
- Reservation Management System
- Video Processing and Storage
- Interactive Dashboard
- Real-time Scheduling
- Conflict Detection for Reservations

## Prerequisites

- Python 3.8 or higher
- MongoDB installed and running
- FFmpeg (for video processing)

## Environment Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd GerenciaCCR
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET_KEY=your_jwt_secret
OPENAI_API_KEY=your_openai_api_key
```

## Running the Application

1. Make sure MongoDB is running

2. Start the application:
```bash
python run.py
```

3. Access the application at `http://localhost:5050`

## Project Structure

- `app.py`: Main application file with route definitions
- `run.py`: Application entry point
- `static/`: Static files (HTML, CSS, JS)
- `app/`: Application modules and components
- `media/`: Storage for uploaded media files
- `requirements.txt`: Project dependencies

## API Endpoints

- `/`: Home page
- `/dashboard`: Main dashboard interface
- `/login`: User authentication
- `/register`: New user registration
- `/api/reservations`: Reservation management
- `/api/video`: Video processing endpoints

## Testing

The project uses pytest for testing. To run the tests:

1. Install test dependencies:
```bash
pip install pytest pytest-cov
```

2. Run the tests:
```bash
pytest
```

3. To run tests with coverage report:
```bash
pytest --cov=src tests/
```

### Test Structure

- `tests/conftest.py`: Contains pytest fixtures used across tests
- `tests/web/`: Tests for web-related functionality
  - `test_app.py`: Tests for app configuration
  - `test_routes.py`: Tests for web routes
- `tests/crews/`: Tests for AI crew functionality
  - `test_crew.py`: Tests for GerenciaCrews class

## Development

The application is built using:
- Flask 3.0.0
- Flask-CORS 4.0.0
- PyMongo 4.6.1
- Flask-JWT-Extended 4.6.0
- OpenAI Whisper
- Google GenerativeAI
- Other dependencies listed in requirements.txt

## License

This project is licensed under the MIT License - see the LICENSE file for details