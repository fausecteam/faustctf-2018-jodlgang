from django.db import migrations
from django.contrib.auth.hashers import UnsaltedMD5PasswordHasher
import string
import random
import json
import os


def replace_umlauts(input):
    return input.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "oe").replace("Ü", "ue").replace("ß", "ss")


def random_password(n=8):
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def create_user_database(apps, schema_editor):
    user_names_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "class_label_mapping_names.json")
    with open(user_names_file, "r") as f:
        user_names = json.load(f)

    User = apps.get_model('jodlplatform', 'User')
    hasher = UnsaltedMD5PasswordHasher()
    for i, name in enumerate(user_names):
        first_name = replace_umlauts(name.split(" ", 1)[0]).lower()
        last_name = replace_umlauts(name.split(" ", 1)[1]).replace(" ", ".").lower()
        email = first_name + "." + last_name + "@jodlgang.com"
        unhashed_password = random_password()
        password = hasher.encode(unhashed_password, salt="")
        User(id=i, name=name, email=email, password=password).save()


class Migration(migrations.Migration):

    dependencies = [
        ('jodlplatform', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user_database)
    ]
