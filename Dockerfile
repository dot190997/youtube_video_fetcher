# init a base image (Alpine is small Linux distro)
FROM python:3.6.1-alpine
# define the present working directory
WORKDIR /youtube_video_fetcher
# copy the contents into the working dir
# exporting PYTHONPATH
RUN export PYTHONPATH="$PYTHONPATH:/app"
ADD . /youtube_video_fetcher
# run pip to install the dependencies of the flask app
RUN pip install -r requirements.txt
# define the command to start the container
CMD ["python","app.py", "-config", "settings/prod_data_config.yml"]