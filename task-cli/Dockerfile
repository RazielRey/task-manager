# Dockerfile for Task CLI
# Used for packaging and distribution

FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY task_cli/ ./task_cli/
COPY setup.py .
COPY README.md .

# Install the CLI tool
RUN pip install -e .

# Set default API URL (can be overridden)
ENV TASK_API_URL=http://task-api:5000

# Default command shows help
CMD ["task", "--help"]