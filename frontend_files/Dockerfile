# Minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Streamlit app and its requirements into the container
COPY . .

# Install Python dependencies listed in requirements.txt
RUN pip3 install -r requirements.txt

# Run Streamlit on port 8501 and make it reachable from outside the container.
# XSRF protection is disabled so CSV uploads (batch prediction) work through the Codespaces tunnel.
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
