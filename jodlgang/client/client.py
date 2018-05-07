import re

import requests


login_csrf_re = re.compile("<input\s+type='hidden'\s+name='csrfmiddlewaretoken'\s+value='([^']*)'\s*/>")


class JodlClient(object):
    def __init__(self, host, port):
        self.url_base = 'http://{host}:{port}'.format(host=host, port=port)
        self.s = requests.Session()

    def login(self, username, password, face_id_path=None):
        resp = self.s.get(self.url_base + '/admin/login/?next=/admin/')
        csrf_token_match = login_csrf_re.search(resp.text)
        if not csrf_token_match:
            raise ValueError("Could not locate CSRF token in response! {}: {}".format(resp.status_code, resp.content))

        csrftoken = csrf_token_match.group(1)

        params = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken)
        files = {}
        if face_id_path is not None:
            img = open(face_id_path, 'rb')
            files['face_img'] = img

        resp = self.s.post(self.url_base + '/admin/login/?next=/admin/', data=params, files=files)
        print("{}: {}".format(resp.status_code, resp.text))
        return resp