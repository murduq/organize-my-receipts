from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import base64
import re

SCOPES = "https://www.googleapis.com/auth/gmail.readonly"
TAG_RE = re.compile(r"<[^>]+>")


def remove_tags(text):
    return TAG_RE.sub("", text)


def get_cost(body):
    """ Parse the body of the email and search for the first found USD amount.

    Parameters
    ----------
    body : string
        email body
    """
    cost = "Unknown"
    try:
        start = body.split("$")[1]
        end_dollar, end_cent = start.split(".")[0], start.split(".")[1][:2]
        cost = "$" + end_dollar + "." + end_cent
    except Exception as e:
        # print(e)
        pass
    return cost


def main():

    store = file.Storage("token.json")
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
        creds = tools.run_flow(flow, store)
    service = build("gmail", "v1", http=creds.authorize(Http()))

    # Call the Gmail API to fetch INBOX
    results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
    messages = results.get("messages", [])

    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        body_contents_base64 = base64.urlsafe_b64decode(
            msg["payload"]["parts"][1]["body"]["data"].encode("ASCII")
        )
        body_contents = remove_tags(str(body_contents_base64))

        # Parsing
        vendor = [i["value"] for i in msg["payload"]["headers"] if i["name"] == "From"][
            0
        ]
        cost = get_cost(body_contents)
        print(vendor, cost)


if __name__ == "__main__":
    main()
