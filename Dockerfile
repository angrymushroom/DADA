# Use an official Python runtime as a parent image
FROM python:3.13-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container at /app
COPY . .

# Expose the port that the FastAPI application will run on
# (Assuming FastAPI runs on port 8000, adjust if different)
EXPOSE 8000

# Command to run the FastAPI application when the container starts
# This is a placeholder for now; we'll refine it later in docker-compose.yml
CMD ["python", "backend/main.py"]
