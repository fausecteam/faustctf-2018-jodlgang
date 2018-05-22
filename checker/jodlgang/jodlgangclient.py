#!/usr/bin/python

import re
import requests
import os
from bs4 import BeautifulSoup
from ctf_gameserver.checker.constants import OK, TIMEOUT, NOTFOUND, NOTWORKING


ERROR_STATUS_CONSTANTS = [TIMEOUT, NOTFOUND, NOTWORKING]


login_csrf_re = re.compile("<input\s+type='hidden'\s+name='csrfmiddlewaretoken'\s+value='([^']*)'\s*/>")
thanks_for_sharing_re = re.compile("<h1\s+class=\"display-5\">Thanks\s+for\s+sharing\s+dude!</h1>")


class JodlGangClient(object):
    def __init__(self, host, port, logger, timeout=None):
        """
        Constructs the base url and initializes the requests session
        :param host: url to JodlGang webservice
        :param port: webserver port
        :param logger: Logger to use
        :param timeout in seconds
        """
        self._url_base = "http://{host}:{port}".format(host=host, port=port)
        self._s = requests.Session()
        self._logger = logger
        self._logged_in = False
        self._timeout = timeout

    @property
    def logged_in(self):
        """
        Accessor for logged in property
        :return:
        """
        return self._logged_in

    @staticmethod
    def _exception_name(exception):
        if isinstance(exception, requests.Timeout):
            return "Timeout"
        elif isinstance(exception, requests.ConnectionError):
            return "Connection error"
        else:
            raise ValueError("Unregistered exception type")

    def login(self, username, face_img_path):
        """
        Uses face authentication to sign in
        :param username: email address of user to sign in
        :param face_img_path: path to image file that shows the user
        :return: status constant
        """

        # Request login page
        try:
            resp = self._s.get(self._url_base + "/login/", timeout=self._timeout)
        except (requests.Timeout, requests.ConnectTimeout) as e:
            self._logger.warning("{} while trying to load login page".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Login page gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        # Check if this looks like the login page
        html_page = resp.text
        if not self._is_login_page(html_page):
            self._logger.warning("This is not the expected login page")
            return NOTWORKING

        # Locate CSRF token
        csrf_token_match = login_csrf_re.search(html_page)
        if not csrf_token_match:
            self._logger.warning("Could not locate CSRF token in login page")
            return NOTWORKING
        csrftoken = csrf_token_match.group(1)

        # Login attempt with face image
        params = dict(username=username, csrfmiddlewaretoken=csrftoken)
        with open(face_img_path, "rb") as f:
            files = {"face_img": f}
            try:
                resp = self._s.post(self._url_base + "/login/", data=params, files=files, timeout=self._timeout)
            except (requests.Timeout, requests.ConnectionError) as e:
                self._logger.warning("{} while trying to log in".format(self._exception_name(e)))
                return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Login attempt gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        if self._is_login_page(resp.text):
            self._logger.warning("Login attempt was unsuccessful, forwarded to login page again")
            return NOTWORKING

        self._logged_in = True
        return OK

    def post_note(self, title, note, public=True):
        """
        Leaves a new note on behalf of the currently signed in user
        :param title: title of the note
        :param note: note text
        :param public: whether this is supposed to be a public or personal note (only visible to the user himself/herself)
        :return: status constant
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            raise RuntimeError("You need to sign in before you can post an advice")

        # Request the write note page
        try:
            resp = self._s.get(self._url_base + "/note/", timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while trying to read add note page".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Add note page gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        # Locate CSRF token
        csrf_token_match = login_csrf_re.search(resp.text)
        if not csrf_token_match:
            self._logger.warning("Could not locate CSRF token in add note page")
            return NOTWORKING
        csrftoken = csrf_token_match.group(1)

        # Post note
        params = dict(title=title, note=note, csrfmiddlewaretoken=csrftoken)
        if public:
            params["public"] = "on"

        try:
            resp = self._s.post(self._url_base + "/note/", data=params, timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while trying to post note".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Could not add note. Post request returned with status code {:d}".format(resp.status_code))
            return NOTWORKING

        thanks_for_sharing_match = thanks_for_sharing_re.search(resp.text)
        if not thanks_for_sharing_match:
            self._logger.warning("Missed the 'Thanks for sharing' response after posting a note")
            return NOTWORKING

        # Note successfully posted
        return OK

    @staticmethod
    def _parse_note(note):
        """
        Parses a note list item
        :param note: bs4 Tag
        :return: dictionary containing title, text, author, and date of the given note, or one of the error status constants if any of these fields could not be found
        """
        title_tag = note.find(class_="title")
        if not title_tag:
            return NOTWORKING

        text_tag = note.find(class_="text")
        if not text_tag:
            return NOTWORKING

        author_tag = note.find(class_="author")
        if not author_tag:
            return NOTWORKING

        date_tag = note.find(class_="date")
        if not date_tag:
            return NOTWORKING

        return {
            "title": title_tag.text,
            "text": text_tag.text,
            "author": author_tag.text,
            "date": date_tag.text
        }

    def _parse_notes_page(self, html_page):
        """
        Parses the notes page, given as raw html text
        :param html_page: html page as string, should contain one element with class notes
        :return:  list of the parsed notes, or on of the error status constants on error
        """
        soup = BeautifulSoup(html_page, "html.parser")
        notes_div = soup.find("div", class_="notes")
        if not notes_div:
            self._logger.warning("Notes div could not be found on public notes page")
            return NOTWORKING

        notes = notes_div.find_all("a", class_="list-group-item")
        if len(notes) == 0:
            return notes

        parsed_notes = []
        for note in notes:
            parsed_note = self._parse_note(note)
            if NOTWORKING == parsed_note:
                self._logger.warning("Error parsing notes")
                return NOTWORKING

            parsed_notes.append(parsed_note)

        return parsed_notes

    @staticmethod
    def _is_login_page(html_page):
        """
        Tells whether the given page is the login page, based on whether it contains the "Please sign in" heading
        :param html_page: html page as string
        :return: True if it seems to be the login page, False otherwise
        """
        soup = BeautifulSoup(html_page, "html.parser")
        heading = soup.find("h1", class_="h3")
        if not heading:
            return False

        if heading.text == "Please sign in":
            return True

        return False

    def list_public_notes(self):
        """
        Grabs the list of public notes
        :return: list of parsed notes, or one of the error status constants on error
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            raise RuntimeError("You need to sign in before you can post an advice")

        # Request the public notes page
        try:
            resp = self._s.get(self._url_base + "/home/", timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while trying to read public notes".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Public notes page gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        # Check if this looks like the login page
        html_page = resp.text
        if self._is_login_page(html_page):
            self._logger.warning("Was unexpectedly forwarded to the login page while trying to view the personal notes")
            return NOTWORKING

        return self._parse_notes_page(html_page)

    def list_personal_notes(self):
        """
        Grabs the list of personal notes
        :return: list of parsed notes, or one of the error status constants on error
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            raise RuntimeError("You need to sign in before you can post an advice")

        # Request the personal notes page
        try:
            resp = self._s.get(self._url_base + "/personal/", timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while trying to read personal notes".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Personal notes page gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        # Check if this looks like the login page
        html_page = resp.text
        if self._is_login_page(html_page):
            self._logger.warning("Was unexpectedly forwarded to the login page while trying to view the personal notes")
            return NOTWORKING

        return self._parse_notes_page(html_page)

    def log_out(self):
        """
        Logs the current user out
        :return: OK on success, one of the error status codes on error
        """
        # Make sure we have signed in successfully
        if not self.logged_in:
            raise RuntimeError("You need to sign in before you can post an advice")

        # Attempt to log out
        try:
            resp = self._s.get(self._url_base + "/logout/", timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while trying to log out".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Logging out gave status code {:d}".format(resp.status_code))
            return NOTWORKING
        
        soup = BeautifulSoup(resp.text, "html.parser")
        if not soup.find("a", class_="login"):
            self._logger.warning("Cannot find login button after logging out")
            return NOTWORKING

        self._logged_in = False
        return OK

    def get_local_ambassador(self):
        """
        Reads the name of the ambassador from the base page's footer
        :return: ambassador name and email as tuple, or NOTWORKING on error
        """
        try:
            resp = self._s.get(self._url_base, timeout=self._timeout)
        except (requests.Timeout, requests.ConnectionError) as e:
            self._logger.warning("{} while reading base url".format(self._exception_name(e)))
            return TIMEOUT

        if resp.status_code != 200:
            self._logger.warning("Requesting base page gave status code {:d}".format(resp.status_code))
            return NOTWORKING

        soup = BeautifulSoup(resp.text, "html.parser")
        ambassador_mailto_tag = soup.find("a", class_="ambassador-email")
        if not ambassador_mailto_tag:
            self._logger.warning("Cannot find ambassador email")
            return NOTWORKING

        ambassador_name = ambassador_mailto_tag.text
        ambassador_email = ambassador_mailto_tag["href"]
        if not ambassador_email.startswith("mailto:"):
            self._logger.warning("Ambassador email does not start with mailto")
            return NOTWORKING
        ambassador_email = ambassador_email[7:]

        return ambassador_name, ambassador_email


if __name__ == "__main__":
    import logging
    logger = logging.getLogger(os.path.basename(__file__))

    client = JodlGangClient("localhost", 8000, logger, timeout=35)
    res = client.login("wenke.schubert@jodlgang.com", "/media/explicat/Moosilauke/ctf/facescrub/training/actresses/faces/Jennifer_Aniston/Jennifer_Aniston_5427_2502_original_noise0.jpeg")
    res = client.post_note("FOMO", "I was afraid of missing out but this changed after joining the Jodlgang!", public=False)
    res = client.list_public_notes()
    res = client.list_personal_notes()
    res = client.log_out()
    # res = client.list_public_notes()
