FROM python:3.11.3

# Set working directory
WORKDIR /data/app

COPY pyproject.toml .
RUN mkdir milkman
COPY milkman/* milkman

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Start the app
CMD ["python", "-m", "milkman"]