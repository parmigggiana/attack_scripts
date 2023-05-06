FROM python:3.11.3

# Set working directory
WORKDIR /data/web

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the app
CMD ["python", "backend.py"]