# Use Python 3.11 slim image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt to the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variables and run the app
CMD gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --threads 1 \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
