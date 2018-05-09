from ctf_gameserver.checker import BaseChecker
from .constants import OK, NOTFOUND, NOTWORKING, TIMEOUT
from .constants import CRYPTO_LINGO
from .jodlgangclient import JodlGangClient
import random


ERROR_CODES = [NOTFOUND, NOTWORKING, TIMEOUT]


class JodlGangChecker(BaseChecker):
    def __init__(self, tick, team, service, ip):
        BaseChecker.__init__(self, tick, team, service, ip)
        self.client = JodlGangClient(service, ip, self.logger)

    def log_in(self, max_attempts=3):
        if self.client.logged_in:
            return OK

        max_attempts = 3
        num_attempts = 0
        # If we haven't managed to log in after `max_attempts`, then we're sick of trying
        while num_attempts < max_attempts:
            # TODO username and face image path
            status = self.client.login(username, face_img_path)
            if OK == status:
                return status

            num_attempts += 1
            self.logger.warning("Login attempt failed for team {}. Status {}. {:d} attemps left".format(self.team, status, max_attempts - num_attempts))

        return status

    def place_flag(self):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to place flag for team {}. Status {}".format(self.team, login_status))
            return login_status

        # Post a note
        title = random.choice(CRYPTO_LINGO)
        text = self.get_flag(str(self.tick))
        post_advice_status = self.client.post_note(title, text, public=False)
        if OK != post_advice_status:
            self.logger.warning("Could not place advice for team {}. Status {}".format(self.team, post_advice_status))

        return post_advice_status

    def check_flag(self, tick):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to check flag for team {}. Status {}".format(self.team, login_status))
            return login_status

        # Retrieve personal notes
        notes = self.client.list_personal_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not retrieve personal notes for team {}. Status {}".format(self.team, notes))
            return notes

        # Find the flag among the personal notes
        flag_to_check = self.get_flag(str(tick))
        notes_containing_the_flag = list(filter(lambda note: note["text"].trim() == flag_to_check, notes))
        num_notes_containing_the_flag = len(notes_containing_the_flag)
        if 0 == num_notes_containing_the_flag:
            self.logger.warning("Could not find flag for team {}".format(self.team))
            return NOTFOUND

        if num_notes_containing_the_flag > 1:
            self.logger.debug("Found more than one occurence of the flag, which seems odd but is acceptable")

        return OK

    def check_service(self):
        # Log in
        login_status = self.log_in()
        if OK != login_status:
            self.logger.warning("Could not log in when trying to check flag for team {}. Status {}".format(self.team, login_status))
            return login_status

        # Retrieve the public notes
        notes = self.client.list_public_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not list public notes for team {}. Status {}".format(self.team, notes))
            return notes

        # Retrieve the personal notes
        notes = self.client.list_personal_notes()
        if notes in ERROR_CODES:
            # At this point notes is actually an error code
            self.logger.warning("Could not list personal notes for team {}. Status {}".format(self.team, notes))
            return notes

        # Log out
        logout_status = self.client.log_out()
        if OK != logout_status:
            self.logger.warning("Could not log out correctly for team {}. Status {}".format(self.team, logout_status))
            return logout_status

        return OK
