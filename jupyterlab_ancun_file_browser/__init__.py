"""
Placeholder
"""
import copy
import json
import logging
import queue

import boto3
import tornado.gen as gen
from notebook.base.handlers import APIHandler
from notebook.utils import url_path_join

#  from dataclasses import dataclass

dirs = [
    {
        'name': 'dir1',
        'type': 'directory',
        'sub': [
            {
                "name": "sub_dir1",
                "type": "directory",
                "sub" : [
                    {
                        "name" : "sub_sub_file1.txt",
                        "type" : "file"
                    }
                ]
            },
            {
                "name": "sub_dir2",
                "type": "directory"
            },
            {
                "name": "sub_file1.txt",
                "type": "file"
            },
            {
                "name": "sub_file2.txt",
                "type": "file"
            }

        ]
    },
    {
        'name': 'dir2',
        'type': 'directory'
    },
    {
        'name': 'dir3',
        'type': 'directory'
    },
    {
        'name': 'dir4',
        'type': 'directory'
    },
    {
        'name': 'file1',
        'type': 'file'
    },
    {
        'name': 'file2.txt',
        'type': 'file'
    },
    {
        'name': 'file3.txt',
        'type': 'file'
    }
]

def get_from_path(path=""):
    path = path.strip('/')
    if path == "":
        return [{"name": tmp["name"], "type": tmp["type"], "path": tmp["name"]} for tmp in dirs]
    else:
        q = queue.Queue()
        tmp_dirs = copy.copy(dirs)
        for p in path.split('/'):
           q.put(p)
        tmp_res = None
        while not q.empty() and (tmp_dirs != None):
            tmp_p = q.get()
            for k in tmp_dirs:
                if tmp_p == k["name"]:
                    tmp_res = k
                    tmp_dirs = tmp_res["sub"] if "sub" in tmp_res else None
        if tmp_res["type"] == "directory" and "sub" in tmp_res:
            return [ {"name": tmp["name"], "type": tmp["type"], "path": path + "/" + tmp["name"]} for tmp in tmp_res["sub"]];
        else:
            return []


class AuthHandler(APIHandler):  # pylint: disable=abstract-method
    """
    handle api requests to change auth info
    """

    @gen.coroutine
    def get(self, path=""):
        self.finish(json.dumps({"authenticated": True}))


class S3Handler(APIHandler):
    """
    Handles requests for getting S3 objects
    """

    s3 = None  # an S3Resource instance to be used for requests

    @gen.coroutine
    def get(self, path=""):
        """
        Takes a path and returns lists of files/objects
        and directories/prefixes based on the path.
        """
        boto3.set_stream_logger("boto3.resources", logging.DEBUG)
        boto3.set_stream_logger("botocore", logging.DEBUG)
        result = get_from_path(path)
        self.finish(json.dumps(result))


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication):
        handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    base_url = web_app.settings["base_url"]
    endpoint = url_path_join(base_url, "s3")
    handlers = [
        (url_path_join(endpoint, "auth") + "(.*)", AuthHandler),
        (url_path_join(endpoint, "files") + "(.*)", S3Handler),
    ]
    web_app.add_handlers(".*$", handlers)
