import logging
from typing import Optional

import requests
from bs4 import BeautifulSoup


def checker(email: str, proxy: str) -> Optional[bool]:
    try:
        assert email and proxy

        proxies = dict(
            http=proxy,
            https=proxy,
        )

        with requests.Session() as session:
            response = session.get(
                "https://accounts.autodesk.com/logon",
                proxies=proxies,
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            form_elem = soup.select_one("#new_user_signin_form")
            assert form_elem, "form not found"
            token_elem = form_elem.select_one('[name="__RequestVerificationToken"]')
            assert token_elem, "token not found"
            token = token_elem.get("value")

            data = {
                "__RequestVerificationToken": token,
                "UserName": email,
                "ForceAuthn": "",
            }

            response = session.post(
                "https://accounts.autodesk.com/Authentication/IsExistingUser",
                data=data,
                proxies=proxies,
            )
            response.raise_for_status()
            data = response.json()
            return data["UserExists"]

    except Exception:
        logging.exception("Failed to check email")
        return None
