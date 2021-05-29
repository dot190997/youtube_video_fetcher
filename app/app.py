from settings.data_config import Config
import argparse
from flask import Flask
from web.routes import routes
from services.youtube_fetcher_football import YoutubeFootball
import nltk


def nltk_downloads():
    nltk.download('stopwords')


def start_server():
    app = Flask(__name__, static_url_path='/fam_pay', static_folder='static')
    app.register_blueprint(routes, url_prefix='/fam_pay')
    app.run(debug=True, host=Config.get_instance().APP_SERVER.HOST, port=Config.get_instance().APP_SERVER.PORT)


def main(config_file_path):
    Config(config_file_path)
    nltk_downloads()
    YoutubeFootball().fetch_videos()
    start_server()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FamPay script")
    parser.add_argument("-config", dest="config_file_path", required=True,
                        help="Enter location of config file")
    args = parser.parse_args()
    main(args.config_file_path)
