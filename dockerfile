# Use an official Python runtime as a parent image
FROM python:3.12.7-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY . /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run migrations and start the Django server
CMD ["sh", "-c", "python3 manage.py runserver 0.0.0.0:8000"]
