# Use slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install system dependencies
# RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*


# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app (make sure this matches your entry point)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
