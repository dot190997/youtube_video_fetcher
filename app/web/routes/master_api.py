from . import routes
from flask import redirect
from flask import render_template
from flask import request
from web.route_support.master_api_support import *
from utils.util import write_api_logs


@routes.route('/healthcheck')
def healthcheck():
    return 'Success'


@routes.route('/get_paginated_data', methods=['GET'])
def get_paginated_data():
    page = request.args.get('page') or 0
    final_result = {'success': True}
    result = None
    try:
        result = MasterAPISupport().fetch_paginated_videos(page)
    except Exception as e:
        final_result['success'] = False
        result = {}
        final_result.setdefault('error', str(e))
    finally:
        final_result.setdefault('result', result)
    write_api_logs(request, final_result)
    return final_result


@routes.route('/get_videos_for_query', methods=['GET'])
def get_videos_for_query():
    query = request.args.get('query')
    top_results = request.args.get('top_results') or 5
    final_result = {'success': True}
    result = None
    try:
        result = MasterAPISupport().get_videos_for_query(query, top_results)
    except Exception as e:
        final_result['success'] = False
        result = {}
        final_result.setdefault('error', str(e))
    finally:
        final_result.setdefault('result', result)
    write_api_logs(request, final_result)
    return final_result

