FROM python:3.12-slim

# Set the working directory
WORKDIR /contest

# Install required Python packages
COPY contest/submission.requirements.txt /contest/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the submission script into the image
COPY contest/submission.py /contest/submission.py

COPY src /contest/src

# Copy model from model folder
COPY onnx /contest/onnx

# The input data file will be mounted at runtime, so no need to include it in the image
# Specify the command to run the solution
CMD ["python", "/contest/submission.py"]