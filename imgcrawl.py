import tmdb
import json
import os
import time
import random
import urllib2

import logging;
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

def save_jdata(filename, data, disp = False):
    f = open(filename, 'w')
    f.write(json.dumps(data))
    f.close()
    if disp:
        logging.info('{} saved'.format(filename))

def load_jdata(filename):
    f = open(filename, 'r')
    content = f.read()
    data = json.loads(content)
    f.close()
    return data

def load_dict(filename):
    return load_jdata(filename) if os.path.exists(filename) else dict()

def load_list(filename):
    return load_jdata(filename) if os.path.exists(filename) else list()

def set_encode(encode='utf-8'):
    import sys
    reload(sys)
    sys.setdefaultencoding(encode)

def catch_httperr(imdb_id):
    response = tmdb.imdb2tmdb(imdb_id)
    j = json.loads(response)
    tmdb_id = ''
    title = ''
    if len(j['movie_results']) > 0:
        if len(j['movie_results']) != 1:
            logging.info('warning: more than 1 movie result for {}'.format(imdb_id))
        info = j['movie_results'][0]
        if info.has_key('id'):
            tmdb_id = info['id']
        if info.has_key('title'):
            title = info['title']
    logging.info('imbd_id = {}, tmdb_id = {}, title = {}'.format(imdb_id, tmdb_id, title))
    return tmdb_id

import csv

def parse_links(filename = '20exp.csv'):
    # parse link file
    tmdb2imdb = dict()
    tmdb2ml = dict()
    missing_list = list()
    first_line = True
    with open(filename) as csv_file:
        reader = csv.reader(csv_file)
        # format: ml_id, imdb_id, tmdb_id
        for line in reader:
            if first_line:
                
                first_line = False
                continue
            if line[-1].isdigit():
                tmdb2imdb[line[-1]] = line[1]
                tmdb2ml[line[-1]] = line[0]
            else:
                missing_list.append(line[0])
    # save missing id list
    filename = 'missing.json'
    save_jdata(filename, missing_list, disp = True)
    return (tmdb2imdb, tmdb2ml)

def crawl_images():
    set_encode()
    tmdb2imdb, tmdb2ml = parse_links()
    # load downloaded data
    filename = 'tmdb-image.json'
    images= load_dict(filename)
    # crawl
    complete_ids = images.keys()
    revise_list = list()
    for tmdb_id in tmdb2imdb.keys():
        if tmdb_id not in complete_ids:
            logging.info('tmdb_id = {}'.format(tmdb_id))
            try:
                response = tmdb.images(tmdb_id)
            except urllib2.HTTPError, e:
                logging.info("HTTPError!")
                imdb_id = tmdb2imdb[tmdb_id]
                revise_list.append((tmdb2ml[tmdb_id], imdb_id, catch_httperr(imdb_id), tmdb_id))
                continue
            j = json.loads(response)
            if j.has_key('posters'):
                images[tmdb_id] = ' '.join([j['posters'][i]['file_path'] for i in range(len(j['posters']))])
            else:
                logging.info('{} no image!'.format(tmdb_id))
            # save intermediate result
            filename = 'tmdb-image.json.cache'
            save_jdata(filename, images, disp = False)
            time.sleep(random.random())
    logging.info('revise information')
    for tup in revise_list:
        print ','.join([str(item) for item in tup])
    # save data
    filename = 'tmdb-image.json'
    save_jdata(filename, images, disp = True)

if __name__ == '__main__':
    import sys
    job_type = 'images'
    if len(sys.argv) > 1:
        job_type = sys.argv[1]
    if job_type == 'images':
        crawl_images()
    else:
        logging.info('unknown job type: {}'.format(job_type))