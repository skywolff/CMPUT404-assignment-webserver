#!/bin/python3
#  coding: utf-8
import socketserver
import os
import urllib.parse
import mimetypes
from http import HTTPStatus

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
        self.command = ""
        self.uri = ""
        self.httpVersion = ""
        self.status = HTTPStatus.OK
        self.responseHeader = ""
        self.responseHeaderParts = []
        self.responseBody = ""


    def handle(self):
        # parse request
        self.data = self.request.recv(1024).strip().decode('utf-8')
        print("Got a request of: \n%s\n" % self.data)
        print("------------------------------------")
        requestHeaders = self.data.split('\r\n')
        requestline = requestHeaders [0]
        self.command, self.uri, self.httpVersion = requestline.split()

        # following block was partially taken from python http.server module
        mname = 'do_' + self.command
        if not hasattr(self, mname):
            # method not handled
            self.status = HTTPStatus.METHOD_NOT_ALLOWED
            self.send_error()
            return
        else:
            method = getattr(self, mname)
            method()


    def do_GET(self):
        path = os.getcwd() + self.uri   # abs path on fs
        if os.path.isdir(path):         # it's a directory => look for index.html
            # print("path is a dir, join index.html")
            index = os.path.join(path, 'index.html')
            if os.path.exists(index):
                path = index
        if not os.path.exists(path):
            self.status = HTTPStatus.NOT_FOUND
            send_error()
            return
        contentType = mimetypes.guess_type(path)[0]
        if contentType:
            # print("content-type : " + str(contentType))
            self.responseHeaderParts.append("Content-type: " + contentType)

        self.assemble_header()
        with open(path, "r") as f:
            self.responseBody = f.read()

        response = "\r\n".join((self.responseHeader, self.responseBody))
        self.request.sendall(bytearray(response,'utf-8'))


    def do_HEAD(self):
        self.assemble_header()
        response = self.responseHeader + "\r\n"
        self.request.sendall(bytearray(response,'utf-8'))

    def assemble_header(self):
        statusLine = " ".join(
            (self.httpVersion, str(self.status.value), self.status.phrase)
        )
        if len(self.responseHeaderParts) != 0:
            self.responseHeaderParts.insert(0, statusLine)
            self.responseHeader = "\r\n".join(self.responseHeaderParts) + "\r\n"
        else:
            self.responseHeader = statusLine + "\r\n"

    # def assemble_response(self):
        # statusLine = " ".join(
            # (self.httpVersion, str(self.status.value), self.status.phrase)
        # )
        # self.responseHeaderParts.insert(0, statusLine)
        # self.response = "\r\n".join(self.responseHeaderParts)
        # response += self.responseBody
        # self.request.sendall(bytearray(response,'utf-8'))


    # def assemble_error(self)
        # response = " ".join(
            # (self.httpVersion, str(self.status.value), self.status.phrase)
        # ) + "\r\n"
        # self.request.sendall(bytearray(response,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080
    os.chdir("./www")               # only serve docs from www dir

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

