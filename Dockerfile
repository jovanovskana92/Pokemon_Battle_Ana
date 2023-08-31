# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /poke.py

# Copy the current directory contents into the container at /app
COPY . /poke.py

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "poke.py"]
