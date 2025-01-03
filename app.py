from flask import Flask, request, jsonify
import docker
import random
import os
import subprocess
import shutil
from functools import wraps

app = Flask(__name__)

# List of Python errors to check for in output
error_list = ['ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException',
              'BlockingIOError', 'BrokenPipeError', 'BufferError', 'BytesWarning',
              'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
              'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning',
              'EOFError', 'Ellipsis', 'EnvironmentError', 'Exception', 'False',
              'FileExistsError', 'FileNotFoundError', 'FloatingPointError',
              'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
              'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError',
              'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
              'MemoryError', 'ModuleNotFoundError', 'NameError', 'None',
              'NotADirectoryError', 'NotImplemented', 'NotImplementedError',
              'OSError', 'OverflowError', 'PendingDeprecationWarning',
              'PermissionError', 'ProcessLookupError', 'RecursionError',
              'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning',
              'StopAsyncIteration', 'StopIteration', 'SyntaxError', 'SyntaxWarning',
              'SystemError', 'SystemExit', 'TabError', 'TimeoutError', 'True',
              'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
              'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
              'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning',
              'ZeroDivisionError']


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.json.get('key') != "snILjFUkk_A":
            return jsonify({"error": "Invalid API key"}), 401
        return view_function(*args, **kwargs)

    return decorated_function


def run_script(image, timeout, code, stdins=""):
    """
    Run Python code in a Docker container
    """
    # Create temporary directory and files
    random_user_dir = f'{random.randint(1000, 2000)}'
    user_dir_url = os.path.join(os.path.dirname(__file__), 'users_task_scripts', random_user_dir)
    os.makedirs(user_dir_url, exist_ok=True)

    # Create the Python script file
    file_url = os.path.join(user_dir_url, 'task.py')
    input_data = "\\n".join(stdins)
    template_code = f'from io import StringIO;import sys;data = "{input_data}";sys.stdin = StringIO(data)\n'

    with open(file_url, "w") as file:
        file.write(template_code)
        file.write(code)

    # Run the code in Docker container
    try:
        client = docker.from_env()
        container = client.containers.run(
            image,
            f'timeout {timeout} python task.py',
            network_disabled=True,
            detach=True,
            remove=False,
            working_dir='/task',
            volumes={user_dir_url: {'bind': '/task', 'mode': 'rw'}}
        )

        answer = container.logs(stream=True)
        container.wait(timeout=int(timeout))
        subprocess.Popen(f"docker rm -f {container.id}", shell=True)

        answer_list = [str(line, "utf-8") for line in answer]

    except Exception as e:
        answer_list = [f"Server error: {str(e)}"]

    finally:
        # Clean up
        shutil.rmtree(user_dir_url)

    # Check for Python errors in output
    error = "None"
    for error_check in error_list:
        if any(error_check in ans for ans in answer_list):
            error = error_check
            break

    return {
        "stdout": "".join(answer_list),
        "error": error
    }


@app.route('/python-ide', methods=['POST'])
@require_api_key
def python_ide():
    """
    API endpoint for running Python code
    Required JSON payload:
    {
        "key": "API_KEY",
        "image": "python:3.x",
        "timeout": "5",
        "code": "print('Hello World')",
        "stdin": ["input1", "input2"] (optional). If there is no input data then just [""]

    }
    """
    try:
        data = request.json
        stdin_list = data.get("stdin", [])
        answer_list = []

        for stdins in stdin_list:
            answer = run_script(
                image=data["image"],
                timeout=data["timeout"],
                code=data["code"],
                stdins=stdins
            )
            answer_list.append(answer)

        return jsonify(answer_list)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == '__main__':
    # Ensure required directory exists
    os.makedirs(os.path.join(os.path.dirname(__file__), 'users_task_scripts'), exist_ok=True)

    app.run(debug=True)