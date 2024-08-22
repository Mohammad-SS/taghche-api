# Dockerfile

# Use the official Python image with slim variant for minimal size.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Set environment variable for unbuffered Python output.
ENV PYTHONUNBUFFERED=1

# Copy the requirements file and install dependencies.
COPY requirements.txt .

# Install required system dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files.
COPY . .

# Expose the port that the app will run on.
EXPOSE 8000
