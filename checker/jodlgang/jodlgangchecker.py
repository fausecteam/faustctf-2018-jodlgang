#!/usr/bin/python


from ctf_gameserver.checker import BaseChecker, OK, NOTFOUND, NOTWORKING, TIMEOUT
from jodlgang.constants import CRYPTO_LINGO
from jodlgang.jodlgangclient import JodlGangClient
import random
import json
import os
import re


# TODO change data dir
DATA_DIR = "/media/explicat/Moosilauke/ctf/facescrub/checker_dataset_non_filtered"
ERROR_CODES = [NOTFOUND, NOTWORKING, TIMEOUT]


class JodlGangChecker(BaseChecker):
    def __init__(self, tick, team, service, ip):
        BaseChecker.__init__(self, tick, team, service, ip)
        self.client = JodlGangClient(service, ip, self.logger)
        self._tick = tick
        self._team = team

        # Read class label to folder mapping
        class_label_mapping_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "class_label_mapping.json")
        class_label_mapping_names_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "class_label_mapping_names.json")

        with open(class_label_mapping_file, "r") as f:
            self._class_label_mapping = json.load(f)

        with open(class_label_mapping_names_file, "r") as f:
            self._class_label_mapping_names = json.load(f)

    @staticmethod
    def _replace_umlauts(input):
        return input.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "oe").replace("Ü", "ue").replace("ß", "ss")

    def _get_user_email_address(self):
        """
        Constructs the user's email address based on the name of the person who is assigned to the given team (based on team id)
        :return: The email address of the identity which is assigned to the given team
        """
        # Get assigned user name based on team id
        name = self._class_label_mapping_names[self._team]
        # Convert user name to email address
        first_name = self._replace_umlauts(name.split(" ", 1)[0]).lower()
        last_name = self._replace_umlauts(name.split(" ", 1)[1]).replace(" ", ".").lower()
        email = first_name + "." + last_name + "@jodlgang.com"
        return email

    def _get_random_user_pic(self):
        """
        Locates one image file for the current user
        :return: path to a face image file that shows the person assigned to the given team
        """
        # Find directory from where to load images
        original_person_name = self._class_label_mapping[self._team]
        original_person_dir = os.path.join(DATA_DIR, original_person_name)
        if not os.path.exists(original_person_dir):
            # If we cannot find the directory, that's an error on our side
            self.logger.error("Directory {} (Team {:d}) could not be found".format(original_person_dir, self._team))
            raise AssertionError()

        # Find all jpg images in this directory
        img_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(original_person_dir) for f in filenames if re.search(".(jpg|jpeg)$", f.lower()) is not None]
        if len(img_files) == 0:
            # If we cannot find any files, that's an error on our side
            self.logger.error("Directory {} (Team {:d}) does not contain any jpg images".format(original_person_dir, self._team))
            raise AssertionError()

        # Randomly select one of the images files
        return random.choice(img_files)

    def log_in(self, max_attempts=3):
        if self.client.logged_in:
            return OK

        username = self._get_user_email_address()
        num_attempts = 0
        # If we haven't managed to log in after `max_attempts`, then we're sick of trying
        while num_attempts < max_attempts:
            face_img_path = self._get_random_user_pic()
            status = self.client.login(username, face_img_path)
            if OK == status:
                return status

            num_attempts += 1
            self.logger.warning("Login attempt failed for team {}. Status {}. {:d} attempts left".format(self._team, status, max_attempts - num_attempts))

        return status

    def place_flag(self):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to place flag for team {}. Status {}".format(self._team, login_status))
            return login_status

        # Post a note
        title = random.choice(CRYPTO_LINGO)
        text = self.get_flag(str(self._tick))
        post_advice_status = self.client.post_note(title, text, public=False)
        if OK != post_advice_status:
            self.logger.warning("Could not place advice for team {}. Status {}".format(self._team, post_advice_status))

        return post_advice_status

    def check_flag(self, tick):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to check flag for team {}. Status {}".format(self._team, login_status))
            return login_status

        # Retrieve personal notes
        notes = self.client.list_personal_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not retrieve personal notes for team {}. Status {}".format(self._team, notes))
            return notes

        # Find the flag among the personal notes
        flag_to_check = self.get_flag(str(tick))
        notes_containing_the_flag = list(filter(lambda note: note["text"].strip() == flag_to_check, notes))
        num_notes_containing_the_flag = len(notes_containing_the_flag)
        if 0 == num_notes_containing_the_flag:
            self.logger.warning("Could not find flag for team {}".format(self._team))
            return NOTFOUND

        if num_notes_containing_the_flag > 1:
            self.logger.debug("Found more than one occurence of the flag, which seems odd but is acceptable")

        return OK

    def check_service(self):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to check flag for team {}. Status {}".format(self._team, login_status))
            return login_status

        # Retrieve the public notes
        notes = self.client.list_public_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not list public notes for team {}. Status {}".format(self._team, notes))
            return notes

        # Retrieve the personal notes
        notes = self.client.list_personal_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not list personal notes for team {}. Status {}".format(self._team, notes))
            return notes

        # Log out
        logout_status = self.client.log_out()
        if OK != logout_status:
            self.logger.warning("Could not log out correctly for team {}. Status {}".format(self._team, logout_status))
            return logout_status

        return OK


if __name__ == "__main__":
    team = 42
    host = "localhost"
    port = 8000
    max_tick = 10
    for tick in range(max_tick):
        checker = JodlGangChecker(tick, team, host, port)
        assert OK == checker.place_flag()
        for check_tick in range(max(0, tick - 5), tick + 1):
            assert OK == checker.check_flag(check_tick)
        assert OK == checker.check_service()
