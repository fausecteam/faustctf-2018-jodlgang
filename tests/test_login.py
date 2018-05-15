from jodlgang.client import JodlGangClient
from jodlgang.data_utils.face_db import available_faces
from jodlgang.data_utils.celeb_labels import get_celeb_labels, get_new_name_labels
import logging

import argparse

log = logging.getLogger('jodlgnag.tests.test_login')

parser = argparse.ArgumentParser()
parser.add_argument('--team-id', default=1, type=int)
parser.add_argument('--img-path-to-use', default=None)

args = parser.parse_args()

dir_fmt_str = '/media/honululu/Data/facescrub_final_directory/training/{type}/faces/{name}/'
celeb_name_mapping = get_celeb_labels()
new_name_mapping = get_new_name_labels()

team_id = args.team_id
celeb_name = celeb_name_mapping[team_id]
new_name = new_name_mapping[team_id]

email = new_name.replace(' ', '.').lower() + '@jodlgang.com'

if args.img_path_to_use is None:
    face_paths = available_faces(celeb_name)
    face_path = face_paths[0]
else:
    face_path = args.img_path_to_use

c = JodlGangClient('localhost', 8000, log)
c.login(username=email, face_img_path=face_path)
print(c)
