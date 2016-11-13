# Purpose: Script to download multiple images async
# Tested with Python 3.5 (Anaconda distro) and AsyncIO 3.4.3

import asyncio
import os
import time
import urllib

import aiohttp
import tqdm

# output dir to store the downloaded images
image_output_folder = os.path.join('downloaded', 'images')
if not os.path.exists(image_output_folder):
    os.makedirs(image_output_folder)

dummy_url_to_image = 'https://dummyimage.com/800/000fff/000000'


# progressbar that I saw on this blog post which also describes a similar workflow as this script
# credit to this post - http://pearcat.tips/2016/01/asyncio-download-multiple-files-asynchronously/
@asyncio.coroutine
def download_images_with_progressbar(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        yield from f


@asyncio.coroutine
def get(*args, **kwargs):
    resp = yield from aiohttp.request('GET', *args, **kwargs)
    # For binary, use .read(), for text use .text() here
    return (yield from resp.read())


@asyncio.coroutine
def download_image(image_url):
    with (yield from rate_limiting_sp):
        response_content = yield from asyncio.async(get(image_url))

    # parse out the original image filename from the original image_url or
    # just use a placeholder like unix time for public distro. to avoid name collision during testing
    # parsed = urllib.parse.urlparse(image_url)
    # this will need to be tweaked for each set of image URLs
    # image_filename = parsed.path.split('/')[3]
    dummy_filename = str(time.time().replace('.', '_'))
    image_filename = dummy_filename
    filename = '{}.jpg'.format(image_filename)
    write_image_to_file_binary(filename, response_content)


def download_images_no_async(list_of_image_urls_to_download):
    for url in list_of_image_urls_to_download:
        dummy_filename = str(time.time().replace('.', '_'))
        filename_nonasync = '{}.jpg'.format(dummy_filename)
        # puts the images in the same dir as the script
        urllib.urlretrieve(url, filename_nonasync)


def write_image_to_file_binary(filename, raw_content):
    with open(os.path.join(image_output_folder, filename), 'wb') as file:
        file.write(raw_content)


rate_limiting_sp = asyncio.Semaphore(50)
image_urls_to_download = [dummy_url_to_image for _ in range(20)]
download_cors = [download_image(image_url) for image_url in image_urls_to_download]

if __name__ == '__main__':
    # the asyncio magic workflow for event loops
    main_event_loop = asyncio.get_event_loop()
    main_event_loop.run_until_complete(download_images_with_progressbar(download_cors))
    main_event_loop.close()
