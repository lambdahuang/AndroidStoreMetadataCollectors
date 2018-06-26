import urllib
import atexit
import logging
import re
import urllib.request
import html
import json
import time

import os
from pathlib import Path

# variable to record the break point
progress_file_path = './scan_progress_google_play.json'
progress_counter = 0

# variable to set the log
logger_format = '%(asctime)-30s %(levelname)-10s %(message)s'
formatter = logging.Formatter(logger_format)
hdlr = logging.FileHandler('./crawler_google_play.log')
hdlr.setFormatter(formatter)

logging.basicConfig(format=logger_format)
logger = logging.getLogger('android-market-crawler')
logger.setLevel(logging.INFO)
logger.addHandler(hdlr)

# application information path
app_directory = './output'


def application_file_loader(file_path):
    try:
        data = json.load(open(file_path))
        return data
    except Exception as e:
        logger.warn('load file [%s] failed' % (file_path))
        return None


def app_name_process(name):
    name = name.replace('/', '-')
    return name


def crawling(app_data):
    try:
        if not app_data['package']:
            return False
        logger.info('process [%s]' % (app_data['package'][0]))
        with urllib.request.urlopen(
            'https://play.google.com/store/apps/details?id=%s' % (app_data['package'][0])
        ) as response:
            html_context = response.read().decode('utf8')
            html_context = str(html_context)
            html_context = html_context.replace('\n', '')
            html_context = html_context.replace('\t', '')
            html_context = html.unescape(html_context)

            # extraction_app_focus = '<c-wiz.*? data-p=.*?%s.*?>(.+?)</c-wiz>' %(app_data['package'][0])
            extraction_app_name = '<h1 class=".*?" itemprop="name"><span.*?>(.+?)</span>'
            extraction_app_score = '<div aria-label="Rated (.+?) stars out of five stars" role="img">'
            extraction_app_rating_num = '<span class="" aria-label=".*? ratings">(.+?)</span>'
            extraction_app_description = '<meta itemprop="description" content="(.+?)">'

            extraction_app_updated = 'Updated</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_version = 'Current Version</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_size = 'Size</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_os = 'Requires Android</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_developer = 'Offered By</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_install = 'Installs</div><span class=".*?"><div><span class=".*?">(.+?)</span></div></span>'
            extraction_app_rating_five = '</span>5</span>.*? aria-label="(.+?) rating'
            extraction_app_rating_four = '</span>4</span>.*? aria-label="(.+?) rating'
            extraction_app_rating_three = '</span>3</span>.*? aria-label="(.+?) rating'
            extraction_app_rating_two = '</span>2</span>.*? aria-label="(.+?) rating'
            extraction_app_rating_one = '</span>1</span>.*? aria-label="(.+?) rating'

            # extraction_app_review_author = '<span class="js5pLc">(.+?)</span>'
            # extraction_app_review_rating = '<div aria-label="Rated (.+?) stars out of five stars" role="img"><div class="vQHuPe bUWb7c"></div><div class="vQHuPe bUWb7c">'
            # extraction_app_review_caption = '<span class="C92E6d">(.+?)</span>'
            # extraction_app_review_content = '<span jsname="bN97Pc">(.+?)</span>'


            # extraction_app_permission = 'This app has access to:</div>(.+?)</div><c-data'

            # pattern_app_focus = re.compile(extraction_app_focus)
            pattern_app_name = re.compile(extraction_app_name)
            pattern_app_score = re.compile(extraction_app_score)
            pattern_app_rating_num = re.compile(extraction_app_rating_num)
            pattern_app_description = re.compile(extraction_app_description)

            pattern_app_updated = re.compile(extraction_app_updated)
            pattern_app_version = re.compile(extraction_app_version)
            pattern_app_size = re.compile(extraction_app_size)
            pattern_app_os = re.compile(extraction_app_os)
            pattern_app_developer = re.compile(extraction_app_developer)
            pattern_app_install = re.compile(extraction_app_install)

            pattern_app_rating_five = re.compile(extraction_app_rating_five)
            pattern_app_rating_four = re.compile(extraction_app_rating_four)
            pattern_app_rating_three = re.compile(extraction_app_rating_three)
            pattern_app_rating_two = re.compile(extraction_app_rating_two)
            pattern_app_rating_one = re.compile(extraction_app_rating_one)

            # pattern_app_review_author = re.compile(extraction_app_review_author)
            # pattern_app_review_rating = re.compile(extraction_app_review_rating)
            # pattern_app_review_caption = re.compile(extraction_app_review_caption)
            # pattern_app_review_content = re.compile(extraction_app_review_content)

            # pattern_app_permission = re.compile(extraction_app_permission)

            app_name = re.findall(pattern_app_name, html_context)
            app_score = re.findall(pattern_app_score, html_context)
            app_rating_num = re.findall(pattern_app_rating_num, html_context)
            app_description = re.findall(pattern_app_description, html_context)

            app_updated = re.findall(pattern_app_updated, html_context)
            app_version = re.findall(pattern_app_version, html_context)

            app_size = re.findall(pattern_app_size, html_context)
            app_os = re.findall(pattern_app_os, html_context)
            app_developer = re.findall(pattern_app_developer, html_context)
            app_install = re.findall(pattern_app_install, html_context)

            app_rating_five = re.findall(pattern_app_rating_five, html_context)
            app_rating_four = re.findall(pattern_app_rating_four, html_context)
            app_rating_three = re.findall(pattern_app_rating_three, html_context)
            app_rating_two = re.findall(pattern_app_rating_two, html_context)
            app_rating_one = re.findall(pattern_app_rating_one, html_context)

            # app_review_author = re.findall(pattern_app_review_author, html_context)
            # app_review_rating = re.findall(pattern_app_review_rating, html_context)
            # app_review_caption = re.findall(pattern_app_review_caption, html_context)
            # app_review_content = re.findall(pattern_app_review_content, html_context)

            # app_permission_raw = re.findall(pattern_app_permission, html_context)

            # print(app_data['package'][0])
            # print(app_name[0])
            # print(html_context)

            """
            print(app_description[0])
            print(app_updated[0])
            print(app_version[0])

            print(app_size[0])
            print(app_os[0])
            print(app_developer[0])

            print(app_install[0])
            print(app_score[0])
            print(app_rating_num[0])
            print(app_rating_five)
            print(app_rating_four)
            print(app_rating_three)
            print(app_rating_two)
            print(app_rating_one)
            """

            # print(app_review_author)
            # print(app_review_rating)
            # print(app_review_caption)
            # print(app_review_content)

            app_info = dict()
            if(app_name):
                app_info['name'] = app_name[0]
            if(app_data['package']):
                app_info['package'] = app_data['package'][0]
            if(app_version):
                app_info['version'] = app_version[0]
            if(app_updated):
                app_info['update'] = app_updated[0]
            if(app_os):
                app_info['os'] = app_os[0]
            if(app_size):
                app_info['size'] = app_size[0]
            if(app_description):
                app_info['description'] = app_description[0]
            if(app_developer):
                app_info['developer'] = app_developer[0]

            app_info['platform'] = dict()
            if(app_score):
                app_info['platform']['score'] = app_score[0]
            if(app_rating_num):
                app_info['platform']['rating_count'] = app_rating_num[0]
            if(app_install):
                app_info['platform']['install_count'] = app_install[0]
            if(app_rating_five):
                app_info['platform']['five_star_count'] = app_rating_five[0]
            if(app_rating_four):
                app_info['platform']['four_star_count'] = app_rating_four[0]
            if(app_rating_three):
                app_info['platform']['three_star_count'] = app_rating_three[0]
            if(app_rating_two):
                app_info['platform']['two_star_count'] = app_rating_two[0]
            if(app_rating_one):
                app_info['platform']['one_star_count'] = app_rating_one[0]

            with open('./output_google/%s.json' % (app_name_process(app_data['package'][0])), 'w') as fileObj:
                json.dump(app_info, fileObj)
            return True
    except Exception as e:
        try:
            logger.warn('process application [%s] failed: %s' % (app_data['package'][0], str(e)))
        except Exception as e:
            logger.warn(str(e))
        finally:
            return False


def iterator():
    global progress_counter
    current_progress = 0
    for root, dirs, files in os.walk(app_directory):
        for file in files:
            if current_progress < progress_counter:
                current_progress = current_progress + 1
            else:
                try:
                    app_file = os.path.join(root, file)
                    app_data = application_file_loader(app_file)
                    ret = crawling(app_data)

                    if ret is False:
                        with open('./only_on_third.txt', 'a') as fileObj:
                            fileObj.write(app_data['package'][0] + '\n')
                    else:
                        with open('./on_both.txt', 'a') as fileObj:
                            fileObj.write(app_data['package'][0] + '\n')

                    current_progress = current_progress + 1
                    progress_counter = current_progress
                    update_progess()
                    time.sleep(.01)
                except Exception as e:
                    logger.warn(str(e))


def update_progess():
    try:
        global progress_counter
        data = dict()
        data['progress'] = progress_counter
        with open(progress_file_path, 'w') as fileObj:
            json.dump(data, fileObj)
    except Exception as e:
        logger.warn('update progress failed. ' + str(e))


def progress_loader():
    log_file = Path(progress_file_path)
    global progress_counter
    progress_counter = 0
    if log_file.is_file():
        try:
            data = json.load(open(progress_file_path))
            progress_counter = int(data['progress'])
            logger.info('load progress succeed.')
        except Exception as e:
            logger.warn('load progress failed. ' + str(e))
    else:
        logger.warn('no progress file.')


def main():
    logger.info('crawler is running.')
    progress_loader()
    iterator()


def shutdown_hook():
    try:
        logger.info('crawler is ending')
        # update_progess()
    except Exception as e:
        logger.warn('error happens when crawler is ending:' + str(e))


if __name__ == '__main__':
    atexit.register(shutdown_hook)
    main()
