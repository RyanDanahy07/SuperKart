# Minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory (app.py, requirements.txt, model) into the container
COPY . .

# Install dependencies without the pip cache to keep the image small
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start the API with Gunicorn: 4 workers, listening on port 7860 on all interfaces.
# "app:superkart_api" = module app.py, Flask instance named superkart_api
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
