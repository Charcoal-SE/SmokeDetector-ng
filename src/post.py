import chat
import html
import json
from typing import TypeVar, Union


class Post:
    _body = ""
    _body_is_summary = False
    _is_answer = False
    _owner_rep = 1
    _parent = None
    _post_id = ""
    _post_score = 0
    _post_site = ""
    _post_url = ""
    _title = ""
    _user_name = ""
    _user_url = ""
    _votes = {'downvotes': None, 'upvotes': None}

    def __init__(self, json_data: str = None, api_response: dict = None, parent: PostType = None) -> None:
        if parent is not None:
            if not isinstance(parent, Post):
                raise TypeError("Parent object for a Post object must also be a Post object.")
            else:
                self._parent = parent

        if json_data is not None:
            self._parse_json_post(json_data)
        elif api_response is not None:
            self._parse_api_post(api_response)
        else:
            raise ValueError("Must provide either JSON Data or an API Response object for Post object.")

        return  # Required for PEP484 compliance

    def __repr__(self) -> str:
        type_name = type(self).__name__
        dataset = ['title=' + self.title, 'body=' + self.body, 'user_name=' + self.user_name,
                   'user_url=' + self.user_url, 'post_site=' + self.post_site, 'post_id=' + self.post_id,
                   'is_answer=' + str(self.is_answer), 'body_is_summary=' + str(self.body_is_summary),
                   'owner_rep=' + str(self.owner_rep), 'post_score=' + str(self.post_score)]
        return "%s(%s)" % (type_name, ', '.join(dataset))

    def _get_title_ignore_type(self) -> str:
        return self.parent.title if self.is_answer else self.title

    def _parse_json_post(self, json_data: str) -> None:
        text_data = json.loads(json_data)["data"]
        if text_data == "hb":
            return

        try:
            data = json.loads(text_data)
        except ValueError:
            chat.tell_rooms_with("debug", "Encountered ValueError parsing the following:\n{0}".format(json_data))
            return
        if "ownerUrl" not in data:
            # owner's account doesn't exist anymore, no need to post it in chat:
            # http://chat.stackexchange.com/transcript/message/18380776#18380776
            return
        self._title = data["titleEncodedFancy"]
        self._title = self._unescape_title(self._title)
        self._body = data["bodySummary"]
        self._user_name = data["ownerDisplayName"]
        self._user_url = data["url"]
        self._post_id = str(data["id"])
        self._post_site = data["siteBaseHostAddress"]
        self._post_site = self._post_site.encode("ascii", errors="replace")
        self._owner_rep = 1
        self._post_score = 0
        self._body_is_summary = True
        self._is_answer = False

        return  # PEP compliance

    def _parse_api_post(self, response: dict) -> None:
        if "title" not in response or "body" not in response:
            return

        self._title = html.unescape(response["title"])
        self._body = html.unescape(response["body"])

        if "IsAnswer" in response and response["IsAnswer"] is True:
            self._is_answer = True
        else:
            if "answers" in response and response["answers"] != []:
                self._answers = []
                for answer in response["answers"]:
                    self._answers.append(Post(api_response=answer))
            else:
                self._answers = []
            self._is_answer = False

        if "BodyIsSummary" in response and response["BodyIsSummary"] is True:
            self._body_is_summary = True
        else:
            self._body_is_summary = False

        if 'site' in response:
            self._post_site = response['site']

        if 'link' in response:
            self._post_url = response["link"]

        if 'score' in response:
            self._post_score = response["score"]

        if 'up_vote_count' in response:
            self._votes['upvotes'] = response["up_vote_count"]

        if 'down_vote_count' in response:
            self._votes['downvotes'] = response["down_vote_count"]

        if 'owner' in response:
            if 'display_name' in response['owner']:
                self._user_name = html.unescape(response["owner"]["display_name"])

            if 'link' in response['owner']:
                self._user_url = response["owner"]["link"]

            if 'reputation' in response['owner']:
                self._owner_rep = response["owner"]["reputation"]
            else:
                self._owner_rep = 0

        # noinspection PyBroadException
        try:
            if 'question_id' in response:
                self._post_id = str(response["question_id"])
            elif 'answer_id' in response:
                self._post_id = str(response["answer_id"])
            else:
                self._post_id = str(0)
        except:
            self._post_id = 0

        return  # PEP compliance

    @staticmethod
    def _unescape_title(title: str) -> str:
        return str(html.unescape(title).strip())

    @property
    def answers(self) -> Union[list, None]:
        # noinspection PyBroadException
        try:
            return self._answers
        except:
            return None

    @property
    def body(self) -> str:
        return str(self._body)

    @property
    def body_is_summary(self) -> bool:
        return bool(self._body_is_summary)

    @property
    def is_answer(self) -> bool:
        return bool(self._is_answer)

    @property
    def owner_rep(self) -> int:
        return int(self._owner_rep)

    @property
    def parent(self) -> PostType:
        return self._parent

    @property
    def post_id(self) -> str:
        return str(self._post_id)

    @property
    def post_score(self) -> int:
        return int(self._post_score)

    @property
    def post_site(self) -> str:
        return str(self._post_site)

    # noinspection PyBroadException
    @property
    def post_url(self) -> object:
        try:
            return str(self._post_url)
        except:
            return "NoLink"

    @property
    def title(self) -> str:
        return str(self._title)

    @property
    def user_link(self) -> str:
        # Alias for self.user_url
        return str(self.user_url)

    @property
    def user_name(self) -> str:
        return str(self._user_name)

    @property
    def user_url(self) -> str:
        return str(self._user_url)

    @property
    def up_vote_count(self) -> object:
        return self._votes['upvotes']

    @property
    def down_vote_count(self) -> object:
        return self._votes['downvotes']

    @property
    def title_ignore_type(self) -> str:
        return self._get_title_ignore_type()

PostType = TypeVar('Post', Post)
