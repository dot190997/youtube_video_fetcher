from settings.data_config import Config
import argparse
from flask import Flask
from web.routes import routes
import nltk
import time
from utils.util import run_io_tasks_in_parallel


def nltk_downloads():
    nltk.download('stopwords')


def start_server():
    app = Flask(__name__, static_url_path='/youtube_video_fetcher', static_folder='static')
    app.register_blueprint(routes, url_prefix='/youtube_video_fetcher')
    app.run(debug=False, host=Config.get_instance().APP_SERVER.HOST, port=Config.get_instance().APP_SERVER.PORT)


def fetch_videos_continuously():
    from services.youtube_fetcher_football import YoutubeFootball
    while True:
        YoutubeFootball().fetch_videos()
        time.sleep(10)


def main(config_file_path):
    Config(config_file_path)
    nltk_downloads()
    run_io_tasks_in_parallel([fetch_videos_continuously, start_server])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FamPay script")
    parser.add_argument("-config", dest="config_file_path", required=True,
                        help="Enter location of config file")
    args = parser.parse_args()
    main(args.config_file_path)
