# youtube_video_fetcher

Steps to run the application (without docker):
1. Change directory to youtube_video_fetcher
2. Export PYTHONPATH = "$PYTHONPATH:/app"
3. create a virtualenv, if needed, and install all the requirements in requirements.txt file
4. Update the config file (app/settings/prod_data_config.yml) as per required
5. Run command: python app/app.py -config settings/prod_data_config.yml


API examples for testing:
1.{{host}}/youtube_video_fetcher/get_paginated_data
2. {{host}}/youtube_video_fetcher/get_paginated_data?page=2
3. {{host}}youtube_video_fetcher/get_videos_for_query?query=messi kenya
4. youtube_video_fetcher/get_videos_for_query?query_type=title&query=WHO IS LEO MESSO? THE NEW FOOTBALL MONSTER FROM KENYA! NEW AFRICAN MESSI