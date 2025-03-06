# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set environment variables to avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including ODBC drivers
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libodbc1 \
    odbcinst1debian2 \
    libodbc2 \ 
    curl \
    gpg

# Debian 12
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list

# optional: for unixODBC development headers
# optional: kerberos library for debian-slim distributions
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    unixodbc-dev libgssapi-krb5-2
    
# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for uvicorn to work inside Docker
ENV HOST=0.0.0.0
ENV PORT=80

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]