import os
from jodlgang.client import JodlClient
from jodlgang.data_utils.face_db import available_faces
from jodlgang.data_utils.celeb_labels import get_celeb_labels, get_new_name_labels
import json

dir_fmt_str = '/media/honululu/Data/facescrub_final_directory/training/{type}/faces/{name}/'
celeb_name_mapping = get_celeb_labels()
new_name_mapping = get_new_name_labels()

team_id = 1
celeb_name = celeb_name_mapping[team_id]
new_name = new_name_mapping[team_id]

email = new_name.replace(' ', '.').lower() + '@jodlgang.com'

import ipdb; ipdb.set_trace()
face_paths = available_faces(celeb_name)
face_path = face_paths[0]

c = JodlClient('localhost', 8000)
c.login(email, 'fearofmissingout', face_id_path=face_path)
print(c)
