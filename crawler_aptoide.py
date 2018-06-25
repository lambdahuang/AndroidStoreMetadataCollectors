import urllib
import atexit
import logging
import re
import urllib.request
import requests
import json
import html
import threading
import time
from pathlib import Path

# logger_format = '%(asctime)-40s %(message)s'
logger_format = '%(asctime)-30s %(levelname)-10s %(message)s'
formatter = logging.Formatter(logger_format)
hdlr = logging.FileHandler('./crawler.log')
hdlr.setFormatter(formatter)

logging.basicConfig(format=logger_format)
logger = logging.getLogger('android-market-crawler')
logger.setLevel(logging.INFO)
logger.addHandler(hdlr)

progress_counter = 0


def shutdown_hook():
    try:
        logger.info('crawler is ending')
        update_progess()
    except Exception as e:
        logger.warn('error happens when crawler is ending:' + str(e))


def application_download(app_url, app_name):
    with urllib.request.urlopen(
        app_url
    ) as response:
        html_context = response.read()
        with open('%s.apk' % (app_name), 'wb') as fileObj:
            fileObj.write(html_context)
    logger.info('file download complete.')


def application_download_page_process(app_url, app_name):
    print (app_url)
    headers = {
        "User-Agent": "Guess who I am",
        "X-Requested-With": "XMLHttpRequest",
        "Pragma": "no-cache",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "http://http://apkins.aptoide.com/",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "http://apkins.aptoide.com/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Cache-Control": "no-cache",
        "Postman-Token": "7aae9a3c-1813-c74f-c7ac-7eb805d8949a"
    }

    response = requests.get(app_url, headers=headers)
    html_context = response.content.decode('utf8')
    html_context = str(html_context)
    html_context = html_context.replace('\n', '')
    html_context = html_context.replace('\t', '')
    html_context = html_context.replace('&amp;', '&')
    extraction_re_apk_url = '<meta http-equiv="refresh" content="1;(.+?)">'
    pattern_app_apk_url = re.compile(extraction_re_apk_url)
    apk_link = re.findall(pattern_app_apk_url, html_context)
    # print(apk_link)
    application_download(apk_link[0], app_name)

    logger.info('file download complete.')


def permission_process(html_context):
    try:
        extraction_re_permissions = '<div class="app-permissions__row"><span>(.+?)</span><span></span></div>'
        pattern_app_apk_permissions = re.compile(extraction_re_permissions)
        permissions = re.findall(pattern_app_apk_permissions, html_context)
        return permissions
    except Exception as e:
        logger.warn('failure in processing permission.')
        return list()


def app_name_process(name):
    name = name.replace('/', '-')
    return name


def review_process(html_context):
    result = list()
    try:
        extraction_re_reviews = '<div class="bundle-item bundle-item--comment">(.+?)<div class="bundle-item__action-bar">'
        extraction_re_reviews_score = '<div class="widget-rating__filled-stars" style="width:(.+?)%;">'
        extraction_re_reviews_writer = '<div class="bundle-item__info"><span class="bundle-item__info__span bundle-item__info__span--bold">(.*?)</span>'
        extraction_re_reviews_title = '<p class="bundle-text--title">(.*?)</p>'
        extraction_re_reviews_content = '<p>(.*?)</p>'

        pattern_app_apk_reviews = re.compile(extraction_re_reviews)
        pattern_app_apk_reviews_score = re.compile(extraction_re_reviews_score)
        pattern_app_apk_reviews_writer = re.compile(extraction_re_reviews_writer)
        pattern_app_apk_reviews_title = re.compile(extraction_re_reviews_title)
        pattern_app_apk_reviews_content = re.compile(extraction_re_reviews_content)
        reviews = re.findall(pattern_app_apk_reviews, html_context)

        for x in reviews:
            score = re.findall(pattern_app_apk_reviews_score, x)
            writer = re.findall(pattern_app_apk_reviews_writer, x)
            title = re.findall(pattern_app_apk_reviews_title, x)
            content = re.findall(pattern_app_apk_reviews_content, x)

            comment = dict()
            comment['writer'] = writer
            comment['title'] = title
            comment['content'] = content
            comment['score'] = score
            result.append(comment)
    except Exception as e:
        logger.warn('Failure in processing review.')
    return result


def application_pages(app_name, app_url):
    logger.info('process [%s] url: %s' % (app_name, app_url))
    try:
        with urllib.request.urlopen(
            app_url
        ) as response:
            html_context = response.read().decode('utf8')
            html_context = str(html_context)
            html_context = html_context.replace('\n', '')
            html_context = html_context.replace('\t', '')
            html_context = html.unescape(html_context)

            extraction_re_download = '<span>Downloads</span><span>(.+?)</span>'
            extraction_re_ver = '<span>Version</span><span.*?>(.+?)</span>'
            extraction_re_score = '<span itemprop="ratingValue">(.+?)</span>'
            extraction_re_description = '<p itemprop="description">(.+?)</p>'
            extraction_re_apk_link = '<div class="header__image"><a href="(.+?)">'
            extraction_re_apk_size = '<span itemprop="fileSize" class="header__store-size">(.+?)</span>'
            extraction_re_permissions = '<div class="popup__content popup__content--app-permissions"><div class="popup-top-bar"><h2>Permissions</h2>(.+?)</div></div>'
            extraction_re_compatibility = '<span itemprop="operatingSystem">(.+?)</span>'
            extraction_re_release_date = '<td>Release date: </td><td>(.+?)</td></tr>'
            extraction_re_support_cpu = '<td>Supported CPU: </td><td><span itemprop="processorRequirements">(.+?)</span></td></tr>'
            extraction_re_package_id = '<td>Package ID: </td><td>(.+?)</td></tr>'
            extraction_re_developer = '<td>Developer.*?</td><td>(.+?)</td></tr>'
            extraction_re_organization = '<td>Organization.*?</td><td>(.+?)</td></tr>'
            extraction_re_locality = '<td>Locality.*?</td><td>(.+?)</td></tr>'
            extraction_re_country = '<td>Country.*?</td><td>(.+?)</td></tr>'
            extraction_re_city = '<td>State/city.*?</td><td>(.+?)</td></tr>'
            extraction_re_reviews = '<div class="bundle__container">(.+?)</div><div class="aptweb-button aptweb-button--see-more">'
            extraction_re_category = '<span itemprop="applicationCategory">(.+?)</span>'

            pattern_app_download = re.compile(extraction_re_download)
            pattern_app_ver = re.compile(extraction_re_ver)
            pattern_app_score = re.compile(extraction_re_score)
            pattern_app_description = re.compile(extraction_re_description)
            pattern_app_apk_link = re.compile(extraction_re_apk_link)
            pattern_app_apk_size = re.compile(extraction_re_apk_size)
            pattern_app_apk_permissions = re.compile(extraction_re_permissions)
            pattern_app_apk_compatibility = re.compile(extraction_re_compatibility)
            pattern_app_apk_release_date = re.compile(extraction_re_release_date)
            pattern_app_apk_support_cpu = re.compile(extraction_re_support_cpu)
            pattern_app_apk_package_id = re.compile(extraction_re_package_id)
            pattern_app_apk_developer = re.compile(extraction_re_developer)
            pattern_app_apk_organization = re.compile(extraction_re_organization)
            pattern_app_apk_locality = re.compile(extraction_re_locality)
            pattern_app_apk_country = re.compile(extraction_re_country)
            pattern_app_apk_city = re.compile(extraction_re_city)
            pattern_app_apk_reviews = re.compile(extraction_re_reviews)
            pattern_app_apk_category = re.compile(extraction_re_category)

            download_count = re.findall(pattern_app_download, html_context)
            ver = re.findall(pattern_app_ver, html_context)
            score = re.findall(pattern_app_score, html_context)
            description = re.findall(pattern_app_description, html_context)
            apk_link = re.findall(pattern_app_apk_link, html_context)
            apk_size = re.findall(pattern_app_apk_size, html_context)
            apk_permissions = re.findall(pattern_app_apk_permissions, html_context)
            apk_compatibility = re.findall(pattern_app_apk_compatibility, html_context)
            apk_release_date = re.findall(pattern_app_apk_release_date, html_context)
            apk_support_cpu = re.findall(pattern_app_apk_support_cpu, html_context)
            apk_package_id = re.findall(pattern_app_apk_package_id, html_context)

            apk_developer = re.findall(pattern_app_apk_developer, html_context)
            apk_organization = re.findall(pattern_app_apk_organization, html_context)
            apk_locality = re.findall(pattern_app_apk_locality, html_context)
            apk_country = re.findall(pattern_app_apk_country, html_context)
            apk_city = re.findall(pattern_app_apk_city, html_context)
            apk_reviews = re.findall(pattern_app_apk_reviews, html_context)
            apk_category = re.findall(pattern_app_apk_category, html_context)

            if len(apk_permissions) > 0:
                permissions = permission_process(apk_permissions[0])
            else:
                permissions = []
            if len(apk_reviews) > 0:
                reviews = review_process(apk_reviews[0])
            else:
                reviews = []

            app_info = dict()
            app_info['name'] = app_name
            app_info['package'] = apk_package_id
            app_info['release_date'] = apk_release_date
            app_info['version'] = ver
            app_info['size'] = apk_size
            app_info['compatibility'] = apk_compatibility
            app_info['support_cpu'] = apk_support_cpu
            app_info['permissions'] = permissions               # list
            app_info['reviews'] = reviews                       # list
            app_info['category'] = apk_category


            app_info['developer'] = dict()
            app_info['developer']['name'] = apk_developer
            app_info['developer']['organization'] = apk_organization
            app_info['developer']['locality'] = apk_locality
            app_info['developer']['country'] = apk_country
            app_info['developer']['city'] = apk_city

            app_info['platform'] = dict()
            if len(score)>0 :
                app_info['platform']['score'] = str(float(score[0]) * 100 / 5)
            else:
                app_info['platform']['score'] = ''
            app_info['platform']['download_count'] = download_count
            app_info['platform']['description'] = description
            app_info['platform']['download_link'] = apk_link

            with open('./output/%s.json' % (app_name_process(app_name)), 'w') as fileObj:
                json.dump(app_info, fileObj)
        return 
    except Exception as e:
        logger.warn('failure in processing [%s] url: %s' % (app_name, app_url))
        return


def crawling(offset):
    try:
        with urllib.request.urlopen(
            'https://en.aptoide.com/apps/local/more?offset=%d' % (offset)
        ) as response:
            html_context = response.read().decode('utf8')
            html_context = str(html_context)
            html_context = html_context.replace('\n', '')
            html_context = html_context.replace('\t', '')
            html_context = html.unescape(html_context)

            extraction_re_application = '<span class="bundle-item__info__span bundle-item__info__span--big">(.+?)</span>'
            extraction_re_app_name = '<a href=".*?">(.+?)</a>'
            extraction_re_app_href = '<a href="(.+?)">'
            pattern_application = re.compile(extraction_re_application)
            pattern_app_name = re.compile(extraction_re_app_name)
            pattern_app_href = re.compile(extraction_re_app_href)
            titles = re.findall(pattern_application, html_context)
            thread_pool = list()

            for x in titles:
                name = re.findall(pattern_app_name, x)
                href = re.findall(pattern_app_href, x)
                """
                if len(name) > 0:
                    print(name[0])
                if len(href) > 0:
                    print(href[0])
                """
                if name and href:
                    try:
                        file_path = './output/%s.json' % (app_name_process(name[0]))
                        log_file = Path(file_path)
                        if not log_file.is_file():
                            thread = threading.Thread(
                                target=application_pages,
                                args=(name[0], href[0])
                            )
                            thread_pool.append(thread)
                            thread.start()
                            time.sleep(.3)
                            # application_pages(name[0], href[0])
                    except Exception as e:
                        logger.warn('processing error' + str(e))
            for x in thread_pool:
                x.join()
        return True
    except Exception as e:
        logger.warn('fetch list failed. ' + str(e))
        time.sleep(5)
        return False


def update_progess():
    try:
        global progress_counter
        data = dict()
        data['progress'] = progress_counter
        with open('./scan_progress.json', 'w') as fileObj:
            json.dump(data, fileObj)
    except Exception as e:
        logger.warn('update progress failed. ' + str(e))


def progress_loader():
    log_file = Path('./scan_progress.json')
    global progress_counter
    progress_counter = 0
    if log_file.is_file():
        try:
            data = json.load(open('./scan_progress.json'))
            progress_counter = int(data['progress'])
            logger.warn('load progress succeed.')
        except Exception as e:
            logger.warn('load progress failed. ' + str(e))
    else:
        logger.warn('no progress file.')


def main():
    logger.info('crawler is running.')
    global progress_counter
    while True:
        # application_pages('cheat Droid','https://foxfi.en.aptoide.com/')
        if(crawling(progress_counter)):
            progress_counter = progress_counter + 30
            update_progess()
        else:
            continue


if __name__ == '__main__':
    atexit.register(shutdown_hook)
    progress_loader()
    main()
