import re
import uuid
from datetime import date
from datetime import datetime, timezone
from multiprocessing import Process
import argparse
import copy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from services.logger import get_logger
import difflib
import hashlib
from concurrent.futures import ThreadPoolExecutor

""" This file contains all the utility functions that can be used in mulitple parts of the project """

STOP_WORDS = set(stopwords.words('english'))
COMMON_WORDS = {'the', 'of', 'a', 'and', 'or', 'for', 'as', 'an', 'to', 'in', 'this', 'be', 'any', 'with'}
STOP_WORDS.update(COMMON_WORDS)
lemmatizer = WordNetLemmatizer()


def run_io_tasks_in_parallel(tasks):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()


def get_hash_value(input_string):
    return hashlib.md5(input_string.encode('utf-8')).hexdigest()


def query_comparator(query1, query2):
    return difflib.SequenceMatcher(None, query1, query2).ratio()


def get_mongo_url(mongo_user, mongo_password, mongo_server, mongo_port):
    return "mongodb://%s:%s@%s:%s" % (mongo_user, mongo_password, mongo_server, mongo_port)


def get_boolean(value) -> bool:
    boolean_value = bool()
    if value is None:
        boolean_value = False
    elif isinstance(value, bool):
        boolean_value = value
    elif isinstance(value, str):
        if value.lower() in {'0', 'false'}:
            boolean_value = False
        else:
            boolean_value = True
    return boolean_value


def is_token_nan(token):
    return not token or token != token


def is_multi_word_token(token):
    return len(token.replace(' ', '_').split('_')) > 1


def clean_string5(s, tokenize=True):
    s = re.sub(r'[-.(),/\\&`~!@#$%^*?"|=+:;]', ' ', s)
    s = re.sub(r'[\']', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = s.strip().lower()
    if tokenize:
        s = re.sub(r'\s+', '_', s)
    else:
        s = re.sub(r'\s+', ' ', s)
    return s


def random_id_generator():
    _id = str(uuid.uuid4())
    return _id


def get_initial_set_field(value, _type):
    initializing_value = set()
    if isinstance(value, _type):
        initializing_value.add(value)
    elif isinstance(value, set) or isinstance(value, list):
        initializing_value = set(value)
    return initializing_value


def write_api_logs(request, response):
    """ Logging all the API requests and responses """
    url = request.url
    method = request.method
    if method == 'POST':
        data = str(request.data)
    else:
        data = str(request.args)

    get_logger('request').info('{}\t{}\t{}'.format(url, data, response.get('success')))
    if not response.get('success'):
        get_logger('errorRequest').info('{}\t{}\t{}'.format(url, data, str(response.get('Error'))))


def get_date(normalized=True):
    if normalized:
        return str(date.today()).replace('-', '')
    return str(date.today())


def get_relevant_word_list(text, reduce=True, normalise=True, lemmatization=True):
    """ normalising the input string, lemmatizing for removing redundancy and removing stop words """
    if normalise:
        text = clean_string5(text, tokenize=True)
        text = text.replace('_', ' ').lower()
    text_list = text.split(' ')
    if reduce:
        remove_words = []
        for word in text_list:
            if len(word) < 2 or word.isnumeric() or word in STOP_WORDS:
                remove_words.append(word)
        for word in remove_words:
            text_list.remove(word)
    if lemmatization:
        for index, word in enumerate(text_list):
            text_list[index] = lemmatizer.lemmatize(word)
    return text_list


def get_rfc_3339_date_format():
    '2021-05-28T14:00:33Z'
    return datetime.now(timezone.utc).isoformat().split('.')[0] + 'Z'


def run_in_parallel(*fns):
    process_list = []
    for fn in fns:
        p = Process(target=fn)
        p.start()
        process_list.append(p)
    for p in process_list:
        p.join()


def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
