import io
import requests
import os
import unittest
import urllib.parse


class Plugin:
    def __init__(self, key, cx):
        self.key = key
        self.cx = cx

    def on_command(self, bot, msg, stdin, stdout, reply):
        query = " ".join(msg["args"][1:])
        if not query:
            query = stdin.read().strip()

        if query:
            url = "https://www.googleapis.com/customsearch/v1?key={0}&cx={1}&q={2}&num=5".format(
                urllib.parse.quote(self.key),
                urllib.parse.quote(self.cx),
                urllib.parse.quote(query)
            )
            headers = {"User-Agent": "SmartBot"}

            res = requests.get(url, headers=headers).json()
            if "error" in res:
                print(res["error"]["message"], file=stdout)
            elif "items" in res:
                for i, item in enumerate(res["items"]):
                    print("[{0}]: {1} - {2}".format(i, item["title"], item["link"]), file=stdout)
            else:
                print("No results!", file=stdout)
        else:
            print(self.on_help(), file=stdout)

    def on_help(self):
        return "Usage: google <query>"


class Test(unittest.TestCase):
    def setUp(self):
        self.plugin = Plugin(os.environ["GOOGLE_SEARCH_KEY"],
                             os.environ["GOOGLE_SEARCH_CX"])

    def test_search(self):
        stdout = io.StringIO()
        self.plugin.on_command(None, {"args": [None, "cat"]}, None, stdout, None)
        self.assertEqual(len(stdout.getvalue().strip().splitlines()), 5)

    def test_no_results(self):
        stdout = io.StringIO()
        self.plugin.on_command(None, {"args": [None, "hosjaiodjsioafsdiofjsio"]}, None, stdout, None)
        self.assertEqual("No results!", stdout.getvalue().strip())

    def test_help(self):
        self.assertTrue(self.plugin.on_help())

    def test_no_args(self):
        stdout = io.StringIO()
        self.plugin.on_command(None, {"args": [None]}, stdout, stdout, None)
        self.assertEqual(self.plugin.on_help(), stdout.getvalue().strip())
