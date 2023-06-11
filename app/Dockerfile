FROM python:3.11.3

# Set working directory
WORKDIR /data/app

RUN apt update && apt install iputils-ping -y

COPY pyproject.toml .
RUN mkdir -p src/milkman
COPY src/milkman/* src/milkman

# Install Python dependencies
RUN pip install --no-cache-dir .



# Start the app
CMD ["python", "-m", "milkman"]