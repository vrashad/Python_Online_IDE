# Python Online Compiler

A secure Flask-based online Python compiler that executes code in isolated Docker containers. This project provides a simple API for running Python code with stdin support and comprehensive error handling.

## Features

- ✨ Isolated code execution in Docker containers
- 🔒 Secure environment with network restrictions
- ⏱️ Execution timeout control
- 📥 Support for stdin inputs
- 🐛 Comprehensive Python error handling
- 🔑 API key authentication

## Prerequisites

- Python 3.x
- Docker
- Flask
- docker-py (Python Docker API)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vrashad/Python_Online_IDE.git
cd Python_Online_IDE
```

2. Install required Python packages:
```bash
pip install flask docker
```

3. Pull the Python Docker image:
```bash
docker pull python:3.9
```

4. Start the Flask server:
```bash
python app.py
```

## API Usage

The compiler exposes a single endpoint that accepts POST requests.

### Endpoint: POST /python-ide

#### Request Format:
```json
{
    "key": "YOUR_API_KEY", # Default: snILjFUkk_A
    "image": "python:3.9",
    "timeout": "5",
    "code": "print('Hello, World!')",
    "stdin": ["input1", "input2"]
}
```

#### Parameters:
- `key` (string, required): API authentication key
- `image` (string, required): Docker Python image to use
- `timeout` (string, required): Maximum execution time in seconds
- `code` (string, required): Python code to execute
- `stdin` (array, optional): Array of input strings for stdin

#### Response Format:
```json
[
    {
        "stdout": "Hello, World!\n",
        "error": "None"
    }
]
```

## Usage Examples

### Simple Example
```python
import requests

url = "http://your-server/python-ide"
payload = {
    "key": "YOUR_API_KEY", # Default: snILjFUkk_A
    "image": "python:3.9",
    "timeout": "5",
    "code": "print('Hello, World!')",
    "stdin": [""]
}

response = requests.post(url, json=payload)
print(response.json())
```

### Example with Input
```python
import requests

code = """
name = input()
age = input()
print(f'Hello, {name}! You are {age} years old.')
"""

payload = {
    "key": "YOUR_API_KEY", # Default: snILjFUkk_A
    "image": "python:3.9",
    "timeout": "5",
    "code": code,
    "stdin": ["Alice", "25"]
}

response = requests.post(url, json=payload)
print(response.json())
```

### Error Handling Example
```python
import requests

code = """
# This will raise a ZeroDivisionError
result = 1 / 0
"""

payload = {
    "key": "YOUR_API_KEY", # Default: snILjFUkk_A
    "image": "python:3.9",
    "timeout": "5",
    "code": code,
    "stdin": [""]
}

response = requests.post(url, json=payload)
print(response.json())
```

## Security Features

- Code execution in isolated Docker containers
- Network access disabled within containers
- Execution timeout limits
- API key authentication
- Automatic cleanup of temporary files
- No filesystem access outside the container

## Error Handling

The compiler detects and reports all standard Python errors, including:
- SyntaxError
- ZeroDivisionError
- NameError
- TypeError
- And many others

## Limitations

- No network access within the executed code
- Limited execution time
- No additional package installation
- Restricted filesystem access
- Single Python version per Docker image

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
