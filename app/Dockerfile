FROM python:3.11.3

# Set working directory
WORKDIR /data/app

RUN apt update && apt install iputils-ping -y

COPY pyproject.toml .
RUN mkdir -p src/
COPY src src/

# Install Python dependencies
RUN pip install .



# Start the app
CMD ["python", "-m", "milkman"]