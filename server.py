#!/usr/bin/env python3
#  coding: utf-8
import socketserver
import os
import posixpath
import mimetypes
from http import HTTPStatus

# Copyright 2019 Alex Li
#
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

class MyWebServer(socketserver.BaseRequestHandler):

    def setup(self):
        self.directory = "www"
        self.method = ""
        self.requestURI = ""
        self.version = "HTTP/1.1"
        self.status = HTTPStatus.OK
        self.responseHeaderParts = []

        # only serve files from directory wwww
        if self.directory not in os.listdir():
            print("%s is not in current directory" % self.directory)
            return


    def handle(self):
        self.data = self.request.recv(1024).strip().decode('utf-8')
        requestLines = self.data.split('\n')
        requestLines = [line.strip().rstrip('\r') for line in requestLines]
        self.method, self.requestURI, self.version = requestLines[0].split()

        # following block refrenced python3 standard library http.server module
        mname = 'do_' + self.method
        if not hasattr(self, mname):
            # method not handled
            self.status = HTTPStatus.METHOD_NOT_ALLOWED
            self.send_header()
            return
        else:
            method = getattr(self, mname)
            method()


    def do_GET(self):
        path = self.directory + posixpath.normpath(self.requestURI)
        if os.path.isdir(path):
            if not self.requestURI.endswith('/'):
                self.status = HTTPStatus.MOVED_PERMANENTLY
                self.responseHeaderParts.append("Location: " + self.requestURI + '/')
                self.send_header()
                return

            # it's a directory => look for index.html
            index = os.path.join(path, 'index.html')
            if os.path.exists(index):
                path = index

        if not os.path.exists(path):
            self.status = HTTPStatus.NOT_FOUND
            self.send_header()
            return

        contentType = mimetypes.guess_type(path)[0]
        if contentType:
            self.responseHeaderParts.append("Content-type: " + contentType)
        self.send_header()
        self.send_body(path)


    def do_HEAD(self):
        self.send_header()


    def send_header(self):
        responseHeader = ""
        statusLine = " ".join(
            (self.version, str(self.status.value), self.status.phrase)
        )
        if len(self.responseHeaderParts) != 0:
            self.responseHeaderParts.insert(0, statusLine)
            responseHeader = "\r\n".join(self.responseHeaderParts) + "\r\n"
        else:
            responseHeader = statusLine + "\r\n"
        responseHeader += "\r\n"
        self.request.sendall(bytearray(responseHeader, 'utf-8'))


    def send_body(self, path):
        responseBody = ""
        with open(path, "r") as f:
            responseBody = f.read()
        self.request.sendall(bytearray(responseBody, 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

