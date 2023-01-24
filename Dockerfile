FROM python3.9

# Install Streamlit and other dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# Add the app files to the image
ADD /src /src

COPY index.html /usr/local/lib/python3.9/site-packages/streamlit/static/index.html

# Set the working directory to the app directory
WORKDIR /src

# Run the app
CMD streamlit run app.py