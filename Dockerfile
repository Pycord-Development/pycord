
# Build Stage ---------------------------------------------------------------
# https://hub.docker.com/_/python
FROM python:3.10.7-slim-bullseye as builder

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install build-essential -y 

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install .[speed] # Speed kills


# Run Stage -----------------------------------------------------------------
FROM python:3.10.7-slim-bullseye

WORKDIR /app

# Copy from the builder stage
COPY --from=builder /app .
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Run the bot
CMD [ "python3", "bot.py" ]
