from PIL import Image
from flask import send_file

from imagetask import ImageTaskApp


def register_imagetask(app, config, route_prefix='',
                       get_endpoint='imagetask_get'):
    imagetask = ImageTaskApp(config)

    @app.route('%s/<data>' % route_prefix, methods=('GET',),
               endpoint=get_endpoint)
    def get(data):
        f = imagetask.from_serial_data(data).generate()
        img = Image.open(f)
        f.seek(0)

        # TODO:
        # Per ssawa:
        # There's a compatibility issue with Python 3's implementation of BytesIO and uwsgi.
        # Imagetask is sending back the data it has using Flask's send_file function which attempts
        # to use the wsgi environ's file wrapper (so that operations like sending local files are optimized)
        # and apparently using a BytesIO file with uwsgi's implementation of the filewrapper no longer works
        # with python 3: https://github.com/unbit/uwsgi/issues/1126
        # (apparently this is an issue with gunicorn as well https://github.com/benoitc/gunicorn/issues/1174).
        # 
        # Rather than using Flask's send_file function here we can just create and return our own
        # response that doesn't use uwsgi's file wrapper.
        # We lose out on the benefits of uwsgi's filewrapper when it does work but this may not make too big of a difference.

        response = make_response(f.read())
        response.headers['Content-Type'] = 'image/%s' % img.format.lower()
        response.mimetype = 'image/%s' % img.format.lower()

        response.headers['Content-Disposition'] = 'attachment; filename=img.%s' % img.format.lower()
        return response

        # Eventually, if there's a fix to the underlying issue, we can delete the manual response and use send_file()
        # return send_file(f, 'image/%s' % img.format.lower())

    return imagetask
