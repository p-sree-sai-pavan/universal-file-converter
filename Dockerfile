# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for FFmpeg, ImageMagick, and unoconv/LibreOffice
# This can be complex and might require specific versions or additional repositories.
# This is a general example, specific packages might vary by distribution.
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    unoconv \
    libreoffice \
    # Clean up after installation to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the working directory
COPY requirements.txt .

# Install any needed Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port your app will run on (Gunicorn defaults to 8000)
EXPOSE 8000

# Define environment variable for unoconv listener if needed
# RUN libreoffice --headless --invisible --norestore --nologo --nofirststartwizard --accept='socket,host=127.0.0.1,port=2002;urp;' &

# Command to run the application (same as Procfile)
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000"]