FROM python:3.8-slim-buster

RUN apt-get update -y
RUN apt install libgl1-mesa-glx wget libglib2.0-0 -y

# Install Streamlit and other dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# Add the app files to the image
ADD . . 

COPY index.html /usr/local/lib/python3.8/site-packages/streamlit/static/index.html

# Set the working directory to the app directory
WORKDIR /src

EXPOSE 8501

# Run the app
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]