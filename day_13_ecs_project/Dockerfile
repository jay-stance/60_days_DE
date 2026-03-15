# 1. Use an official, lightweight Linux Python environment
FROM python:3.12-slim

# 2. Create a folder inside the container to hold our code
WORKDIR /app

# 3. Copy our Python script from your Mac into the container
COPY processor.py .

# 4. Tell the container what command to run when AWS boots it up
CMD ["python", "processor.py"]