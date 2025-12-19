# Mr.Debug

A web-based Python code execution service that provides intelligent error explanations for Python learners.

(The project is heavily assisted by AI)

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

## Overview

Mr.Debug is designed to help beginners learn Python by transforming cryptic error messages into clear, actionable explanations. The application runs Python code in a secure, isolated environment and provides detailed feedback on both successful executions and errors.

### Key Features

- **Secure Code Execution**: Runs Python code in isolated subprocesses with configurable timeout protection
- **Intelligent Error Analysis**: Provides human-readable explanations for common Python errors
- **Input Handling**: Supports programs that require standard input via `input()` function
- **RESTful API**: Clean API design enabling integration with other educational tools
- **Modern Web Interface**: Responsive, professional UI for writing and testing code
- **Extensible Architecture**: Modular design allows easy addition of new error patterns and AI integration

## Table of Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Error Detection](#error-detection)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Architecture

The application consists of three main components:

### Backend (FastAPI)

- **main.py**: Core application server handling HTTP requests and code execution
- **error_handling.py**: Error interpretation engine with pattern matching and optional AI integration

### Frontend

- **index.html**: Single-page application providing the user interface

### Design Principles

- Separation of concerns between execution and error interpretation
- Fail-safe fallback from AI to pattern-based error detection
- Security-first approach with subprocess isolation and timeout limits

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Step-by-Step Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mrdebug.git
cd mrdebug
```

2. Install required dependencies:
```bash
pip install fastapi uvicorn
```

3. Verify installation:
```bash
python -c "import fastapi; import uvicorn; print('Installation successful')"
```

## Usage

### Starting the Server

#### Basic Usage

```bash
uvicorn Backend.main:app --host 0.0.0.0 --port 8000
```

#### Development Mode (with auto-reload)

```bash
uvicorn Backend.main:app --reload
```

#### Using the Python Module Directly

```bash
python -m Backend.main
```

### Accessing the Application

Once the server is running, open your web browser and navigate to:

```
http://localhost:8000
```

### Using the Web Interface

1. Write or paste Python code in the editor
2. (Optional) Provide input for programs using `input()` in the "Program input" field
3. (Optional) Adjust the timeout duration (1-60 seconds)
4. Click "Run Code" or press Ctrl+Enter (Cmd+Enter on Mac)
5. View results and error explanations in the results panel

### Example Usage

**Successful Execution:**
```python
print("Hello, World!")
```

**Error with Explanation:**
```python
print(x)  # NameError with detailed explanation
```

**Program with Input:**
```python
name = input("Enter your name: ")
print(f"Hello, {name}!")
```

## API Documentation

### Execute Code Endpoint

**Endpoint:** `POST /run`

**Description:** Executes Python code and returns results or error explanations.

#### Request Schema

```json
{
  "code": "string (required, min_length=1)",
  "stdin": "string (optional, default='')",
  "timeout": "integer (optional, default=10, range=1-60)"
}
```

#### Response Schema

**Success Response:**
```json
{
  "status": "success",
  "output": "string",
  "error": null,
  "explanation": null,
  "execution_time": 0.123
}
```

**Error Response:**
```json
{
  "status": "error",
  "output": null,
  "error": "string (raw error message)",
  "explanation": {
    "summary": "string (brief explanation)",
    "why_it_happened": "string (detailed cause)",
    "how_to_fix": ["array of fix suggestions"],
    "corrected_example": "string or null",
    "confidence": 0.95
  },
  "execution_time": 0.056
}
```

### Health Check Endpoint

**Endpoint:** `GET /health`

**Description:** Returns server health status.

**Response:**
```json
{
  "service": "Code Execution Service",
  "status": "running",
  "endpoint": "/run"
}
```

### Frontend Endpoint

**Endpoint:** `GET /`

**Description:** Serves the web interface.

### Example cURL Requests

**Basic Code Execution:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello, World!\")",
    "timeout": 5
  }'
```

**With Standard Input:**
```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "code": "name = input(\"Name: \")\nprint(f\"Hello, {name}\")",
    "stdin": "Alice",
    "timeout": 5
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Enable auto-reload (dev mode) | `true` |

### Azure OpenAI Integration (Optional)

For AI-powered error explanations, configure the following environment variables:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_DEPLOYMENT="your-deployment-name"
```

When these variables are set, the system will use Azure OpenAI for enhanced error explanations. Without them, the application falls back to pattern-based error detection.

### Security Considerations

- **Timeout Limits**: Execution time is capped between 1-60 seconds
- **Process Isolation**: Code runs in separate subprocess with no system access
- **CORS Configuration**: Currently set to allow all origins (configure for production)
- **Input Validation**: Pydantic models enforce request schema validation

## Error Detection

### Built-in Error Patterns

The system recognizes and explains the following error types:

#### NameError
- **Detection**: Variable used before definition
- **Explanation**: Identifies undefined variables and typos
- **Confidence**: 95%

#### ZeroDivisionError
- **Detection**: Division or modulo by zero
- **Explanation**: Explains mathematical undefined operations
- **Confidence**: 95%

#### SyntaxError
- **Detection**: Invalid Python syntax
- **Explanation**: Points to common syntax mistakes
- **Confidence**: 85%

#### TimeoutError
- **Detection**: Execution exceeds timeout or missing input
- **Special Handling**: Distinguishes between infinite loops and missing `input()` data
- **Confidence**: 95%

### Adding Custom Error Patterns

To add new error patterns, modify `Backend/error_handling.py`:

```python
def _fallback_explain(error: str) -> dict:
    error_lower = error.lower()
    
    # Add your pattern here
    if "your_error_pattern" in error_lower:
        return {
            "summary": "Brief explanation",
            "why_it_happened": "Detailed cause",
            "how_to_fix": ["Step 1", "Step 2"],
            "corrected_example": "correct_code_here",
            "confidence": 0.90
        }
    
    # ... existing patterns
```

## Development

### Project Structure

```
mrdebug/
├── Backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   └── error_handling.py       # Error interpretation logic
├── Frontend/
│   └── index.html             # Web interface
├── README.md
├── requirements.txt
└── .gitignore
```

### Development Workflow

1. **Make Changes**: Edit source files in `Backend/` or `Frontend/`
2. **Test Locally**: Run with `--reload` flag for auto-restart
3. **Test API**: Use cURL, Postman, or the web interface
4. **Commit**: Follow conventional commit messages

### Running Tests

**Manual API Testing:**
```bash
# Test successful execution
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "print(2 + 2)"}'

# Test error handling
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "print(undefined_variable)"}'

# Test timeout
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"code": "while True: pass", "timeout": 2}'
```

### Code Style

The project follows PEP 8 guidelines for Python code. Key conventions:

- Use type hints where applicable
- Maximum line length: 100 characters
- Docstrings for all public functions
- Clear variable and function names

## Deployment

### Production Recommendations

1. **Web Server**: Use Gunicorn or uWSGI with Uvicorn workers
2. **Reverse Proxy**: Deploy behind Nginx or Apache
3. **HTTPS**: Enable SSL/TLS certificates
4. **CORS**: Restrict origins to your frontend domain
5. **Rate Limiting**: Implement request throttling
6. **Monitoring**: Add logging and health check monitoring

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Backend/ ./Backend/
COPY Frontend/ ./Frontend/

EXPOSE 8000

CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t mrdebug .
docker run -p 8000:8000 mrdebug
```

### Cloud Deployment

**Heroku:**
```bash
heroku create your-app-name
git push heroku main
```

**AWS/GCP/Azure:**
- Use containerized deployment with Docker
- Configure environment variables via platform secrets management
- Set up auto-scaling based on request load

## Contributing

Contributions are welcome! Please follow these guidelines:

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution

- **Error Patterns**: Add detection for more Python error types
- **AI Integration**: Enhance Azure OpenAI implementation
- **UI/UX**: Improve frontend design and user experience
- **Documentation**: Expand examples and tutorials
- **Testing**: Add unit tests and integration tests
- **Security**: Enhance sandboxing and input validation
- **Features**: Code suggestions, syntax highlighting, code sharing

### Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. Consult GitHub Help for more information on using pull requests.

## Roadmap

Future enhancements planned:

- [ ] Unit test suite with pytest
- [ ] Syntax highlighting in code editor
- [ ] Code sharing via unique URLs
- [ ] User authentication and saved code snippets
- [ ] Multiple language support (JavaScript, Java, etc.)
- [ ] Real-time collaboration features
- [ ] Integration with educational platforms
- [ ] Enhanced AI-powered code suggestions


## Acknowledgments

- FastAPI framework for the excellent API development experience
- Python community for comprehensive error documentation
- Contributors and users providing feedback and improvements

## Support

For issues, questions, or suggestions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/mrdebug/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mrdebug/discussions)
- **Email**: your.email@example.com

## Changelog

### Version 1.0.0 (Current)

- Initial release
- Basic error detection for common Python errors
- Web interface for code execution
- RESTful API with timeout protection
- Optional Azure OpenAI integration
