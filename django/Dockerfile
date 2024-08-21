# Dockerfile

# Use the official Python image with slim variant for minimal size.
FROM python:3.11-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .

# Install required system dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files.
COPY . .

# Expose the port that the app will run on.
EXPOSE 8000

# Command to run the Django application.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
