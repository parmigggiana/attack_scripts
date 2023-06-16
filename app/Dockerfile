FROM python:3.11.3

# Set working directory
WORKDIR /data/app

RUN apt update && apt install iputils-ping -y

COPY pyproject.toml .

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install milkman
COPY src src/
RUN pip install .

# Start the app
CMD ["python", "-m", "milkman"]