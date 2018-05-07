import os
from client import JodlClient
from face_db import available_faces
import json

dir_fmt_str = '/media/honululu/Data/facescrub_final_directory/training/{type}/faces/{name}/'
mapping = json.load(open('../src/jodlgang/class_label_mapping.json'))

team_id = 3
user_name = mapping[team_id]

face_paths = available_faces(user_name)
face_path = face_paths[0]

c = JodlClient('localhost', 8000)
c.login('wenke.schubert@jodlgang.com', 'fearofmissingout', face_id_path=face_path)
print(c)