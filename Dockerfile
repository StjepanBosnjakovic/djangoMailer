# Use the official Python image as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip --no-cache-dir --progress-bar off
RUN pip install --no-cache-dir -r requirements.txt gunicorn --progress-bar off

# Copy the entire project into the container
COPY . /app/

RUN python manage.py migrate
RUN python manage.py createsuperuser --noinput || true
# Expose port 8000 for the Django app
EXPOSE 8000

# Command to run when starting the container
CMD ["gunicorn", "djangoMailer.wsgi:application", "--bind", "0.0.0.0:8000"]