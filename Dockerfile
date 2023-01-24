FROM nikolaik/python-nodejs:python3.9-nodejs18

# Install Streamlit and other dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# Add the app files to the image
ADD /src /src
ADD index.html index.html

# ADD index.html /usr/local/lib/python3.9/site-packages/streamlit/static/index.html
COPY index.html /usr/local/lib/python3.9/site-packages/streamlit/static/index.html

# Set the working directory to the app directory
WORKDIR /src

EXPOSE 8501

# Run the app
ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py", "--server.headless", "true", "--server.fileWatcherType", "none", "--browser.gatherUsageStats", "false"]