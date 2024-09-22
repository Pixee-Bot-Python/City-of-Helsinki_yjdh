import logging
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from rest_framework.exceptions import PermissionDenied, ValidationError

from events.exceptions import LinkedEventsException
from security import safe_requests

LOGGER = logging.getLogger(__name__)


class LinkedEventsClient:
    def __init__(self):
        if not all(
            [
                settings.LINKEDEVENTS_URL,
                settings.LINKEDEVENTS_API_KEY,
                settings.LINKEDEVENTS_TIMEOUT,
            ]
        ):
            raise ValueError("LinkedEvents client settings not configured.")

    def _headers(self):
        return {
            "content-type": "application/json",
            "accept": "application/json",
            "apikey": settings.LINKEDEVENTS_API_KEY,
        }

    def _api_call(
        self, requests_method, resource, resource_id=None, params=None, json=None
    ):
        url = (
            settings.LINKEDEVENTS_URL
            if settings.LINKEDEVENTS_URL.endswith("/")
            else settings.LINKEDEVENTS_URL + "/"
        )
        url += resource + "/"
        if resource_id is not None:
            url += resource_id + "/"

        try:
            r = requests_method(
                url,
                json=json,
                params=params,
                headers=self._headers(),
                timeout=settings.LINKEDEVENTS_TIMEOUT,
            )
            r.raise_for_status()
        # TODO add logging for errors
        except ConnectionError:
            raise LinkedEventsException(
                code=503, detail="Error connecting to Linked Events (ConnectionError)."
            )
        except Timeout:
            raise LinkedEventsException(
                code=503, detail="Timeout exceeded when connecting to Linked Events."
            )
        except HTTPError as e:
            if e.response.status_code >= 500:
                # This is probably an HTML response instead of a JSON response,
                # thus we don't try to get the response body
                # TODO in some cases it would be helpful to inspect this body to find
                # where the error originates (a forgotten slash has been seen while testing)
                raise LinkedEventsException(
                    code=503, detail="Server error from Linked Events."
                )
            # TODO 403 is actually configuration error in Linked Events for the TET API key
            elif e.response.status_code == 401 or e.response.status_code == 403:
                raise LinkedEventsException(
                    code=500,
                    detail="Linked Events API key misconfiguration in backend.",
                )
            else:
                raise LinkedEventsException(
                    code=e.response.status_code, response_data=e.response.json()
                )
        except RequestException:
            raise LinkedEventsException(code=503)
        else:
            return r.json()

    def list_ongoing_events_authenticated(self, publisher=None, text=None):
        events = []
        nexturl = None
        while True:
            if nexturl:
                r = safe_requests.get(nexturl, headers=self._headers())
            else:
                params = {
                    "data_source": "tet",
                    "nocache": True,
                    "show_all": True,
                }
                if publisher:
                    params["publisher_ancestor"] = publisher

                if text:
                    params["text"] = text

                r = safe_requests.get(
                    urljoin(settings.LINKEDEVENTS_URL, "event/"),
                    headers=self._headers(),
                    params=params,
                )

            # TODO this doesn't use error handling from _api_call
            r.raise_for_status()
            data = r.json()
            events += data["data"]
            if data["meta"]["next"] is not None:
                nexturl = data["meta"]["next"]
            else:
                break

        return events

    def get_event(self, event_id):
        params = {
            "data_source": "tet",
            "nocache": True,
            "include": "location,keywords",
        }
        return self._api_call(
            requests_method=requests.get,
            resource="event",
            resource_id=event_id,
            params=params,
        )

    def create_event(self, event):
        return self._api_call(
            requests_method=requests.post,
            resource="event",
            json=event,
        )

    def delete_event(self, id):
        # TODO this doesn't use error handling from _api_call
        params = {
            "data_source": "tet",
            "nocache": True,
        }
        r = requests.delete(
            urljoin(settings.LINKEDEVENTS_URL, "event/" + id),
            headers=self._headers(),
            params=params,
        )
        return r.status_code

    def update_event(self, eventid, event):
        return self._api_call(
            requests_method=requests.put,
            resource="event",
            resource_id=eventid,
            json=event,
        )

    def get_url(self, url):
        # TODO check that url.startswith(settings.LINKEDEVENTS_URL)
        r = safe_requests.get(url, headers=self._headers())
        # TODO better error handling
        r.raise_for_status()
        return r.json()

    def upload_image(self, body, files):
        r = requests.post(
            urljoin(settings.LINKEDEVENTS_URL, "image/"),
            headers={"apikey": settings.LINKEDEVENTS_API_KEY},
            data=body,
            files=files,
        )
        try:
            r.raise_for_status()
        except HTTPError as e:
            if e.response.status_code == 400:
                raise ValidationError(detail="File not accepted")
            else:
                raise PermissionDenied(detail="Could not upload")
        except RequestException:
            raise LinkedEventsException(code=503)
        return r.json()

    def update_image(self, image_id, image):
        return self._api_call(
            requests_method=requests.put,
            resource="image",
            resource_id=image_id,
            json=image,
        )

    def delete_image(self, id):
        params = {
            "data_source": "tet",
            "nocache": True,
        }
        r = requests.delete(
            urljoin(settings.LINKEDEVENTS_URL, f"image/{id}"),
            headers=self._headers(),
            params=params,
            timeout=settings.LINKEDEVENTS_TIMEOUT,
        )
        return r.status_code

    def get_images(self):
        """
        Used by the job clean_unused_images

        Returns a generator that yields one page of images at a time.
        """
        r = safe_requests.get(
            urljoin(settings.LINKEDEVENTS_URL, "image/"),
            params={
                "data_source": "tet",
                "nocache": True,
            },
            timeout=settings.LINKEDEVENTS_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        yield data["data"]

        while data["meta"]["next"] is not None:
            r = safe_requests.get(
                data["meta"]["next"], timeout=settings.LINKEDEVENTS_TIMEOUT
            )
            r.raise_for_status()
            data = r.json()
            yield data["data"]
