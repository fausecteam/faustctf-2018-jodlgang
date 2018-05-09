import re
import requests
import os
from bs4 import BeautifulSoup


login_csrf_re = re.compile("<input\s+type='hidden'\s+name='csrfmiddlewaretoken'\s+value='([^']*)'\s*/>")
thanks_for_sharing_re = re.compile("<h1\s+class=\"display-5\">Thanks\s+for\s+sharing\s+dude!</h1>")


class JodlGangClient(object):
    def __init__(self, host, port, logger):
        """
        Constructs the base url and initializes the requests session
        :param host: url to JodlGang webservice
        :param port: webserver port
        :param logger: Logger to use
        """
        self.url_base = "http://{host}:{port}".format(host=host, port=port)
        self.s = requests.Session()
        self.logger = logger
        self.logged_in = False

    def login(self, username, face_img_path):
        """
        Uses face authentication to sign in
        :param username: email address of user to sign in
        :param face_img_path: path to image file that shows the user
        :return: True if login was successful, False on error
        """

        # Request login page
        resp = self.s.get(self.url_base + "/login/")
        if resp.status_code != 200:
            self.logger.warning("Login page gave status code {:d}".format(resp.status_code))
            return False

        # Check if this looks like the login page
        html_page = resp.text
        if not self._is_login_page(html_page):
            self.logger.warning("This is not the expected login page")
            return False

        # Locate CSRF token
        csrf_token_match = login_csrf_re.search(html_page)
        if not csrf_token_match:
            self.logger.warning("Could not locate CSRF token in login page")
            return False
        csrftoken = csrf_token_match.group(1)

        # Login attempt
        params = dict(username=username, csrfmiddlewaretoken=csrftoken)
        with open(face_img_path, "rb") as f:
            files = {"face_img": f}
            resp = self.s.post(self.url_base + "/login/", data=params, files=files)

        if resp.status_code != 200:
            self.logger.warning("Login attempt gave status code {:d}".format(resp.status_code))
            return False

        self.logged_in = True
        return True

    def post_advice(self, title, text, public=True):
        """
        Leaves a new note on behalf of the currently signed in user
        :param title: title of the note
        :param text: note text
        :param public: whether this is supposed to be a public or personal note (only visible to the user himself/herself)
        :return: True if note was left successfully, False otherwise
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            self.logger.warning("You need to sign in before you can post an advice")
            return False

        # Request the write note page
        resp = self.s.get(self.url_base + "/note/")
        if resp.status_code != 200:
            self.logger.warning("Add note page gave status code {:d}".format(resp.status_code))
            return False

        # Locate CSRF token
        csrf_token_match = login_csrf_re.search(resp.text)
        if not csrf_token_match:
            self.logger.warning("Could not locate CSRF token in add note page")
            return False
        csrftoken = csrf_token_match.group(1)

        # Post your advice
        params = dict(title=title, text=text, csrfmiddlewaretoken=csrftoken)
        if public:
            params["public"] = "on"
        resp = self.s.post(self.url_base + "/note/", data=params)
        if resp.status_code != 200:
            self.logger.warning("Could not add note. Post request returned with status code {:d}".format(resp.status_code))
            return False

        thanks_for_sharing_match = thanks_for_sharing_re.search(resp.text)
        if not thanks_for_sharing_match:
            self.logger.warning("Missed the 'Thanks for sharing' response after posting a note")
            return False

        # Note successfully posted
        return True

    @staticmethod
    def _parse_note(note):
        """
        Parses a note list item
        :param note: bs4 Tag
        :return: dictionary containing title, text, author, and date of the given note, False if any of these fields could not be found
        """
        title_tag = note.find(class_="title")
        if not title_tag:
            return False

        text_tag = note.find(class_="text")
        if not text_tag:
            return False

        author_tag = note.find(class_="author")
        if not author_tag:
            return False

        date_tag = note.find(class_="date")
        if not date_tag:
            return False

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
        :return:  list of the parsed notes, or False on error
        """
        soup = BeautifulSoup(html_page, "html.parser")
        notes_div = soup.find("div", class_="notes")
        if not notes_div:
            self.logger.warning("Notes div could not be found on public notes page")
            return False

        notes = notes_div.find_all("a", class_="list-group-item")
        if len(notes) == 0:
            return notes

        parsed_notes = []
        for note in notes:
            parsed_note = self._parse_note(note)
            if False == parsed_note:
                self.logger.warning("Error parsing notes")
                return False

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
        :return: list of parsed notes, or False on error
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            self.logger.warning("You need to sign in before you can post an advice")
            return False

        # Request the public notes page
        resp = self.s.get(self.url_base + "/home/")
        if resp.status_code != 200:
            self.logger.warning("Public notes page gave status code {:d}".format(resp.status_code))
            return False

        # Check if this looks like the login page
        html_page = resp.text
        if self._is_login_page(html_page):
            self.logger.warning("Was unexpectedly forwarded to the login page while trying to view the personal notes")
            return False

        return self._parse_notes_page(html_page)

    def list_personal_notes(self):
        """
        Grabs the list of personal notes
        :return: list of parsed notes, or False on error
        """

        # Make sure we have signed in successfully
        if not self.logged_in:
            self.logger.warning("You need to sign in before you can post an advice")
            return False

        # Request the personal notes page
        resp = self.s.get(self.url_base + "/personal/")
        if resp.status_code != 200:
            self.logger.warning("Personal notes page gave status code {:d}".format(resp.status_code))
            return False

        # Check if this looks like the login page
        html_page = resp.text
        if self._is_login_page(html_page):
            self.logger.warning("Was unexpectedly forwarded to the login page while trying to view the personal notes")
            return False

        return self._parse_notes_page(html_page)

    def log_out(self):
        # Make sure we have signed in successfully
        if not self.logged_in:
            self.logger.warning("You need to sign in before you can post an advice")
            return False

        resp = self.s.get(self.url_base + "/logout/")
        if resp.status_code != 200:
            self.logger.warning("Logging out gave status code {:d}".format(resp.status_code))
            return False
        
        soup = BeautifulSoup(resp.text, "html.parser")
        if not soup.find("a", class_="login"):
            self.logger.warning("Cannot find login button after logging out")
            return False

        self.logged_in = False
        return True


if __name__ == "__main__":
    import logging
    logger = logging.getLogger(os.path.basename(__file__))

    client = JodlGangClient("localhost", 8000, logger)
    res = client.login("wenke.schubert@jodlgang.com", "/media/explicat/Moosilauke/ctf/facescrub/training/actresses/faces/Jennifer_Aniston/Jennifer_Aniston_5427_2502_original_noise0.jpeg")
    # res = client.post_advice("FOMO", "I was afraid of missing out but this changed after joining the Jodlgang!", public=False)
    res = client.list_public_notes()
    res = client.list_personal_notes()
    res = client.log_out()
    res = client.list_public_notes()