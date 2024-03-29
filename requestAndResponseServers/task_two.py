#!/usr/bin/env python3

import socket
import sys
import os
import datetime

PORT = 8080
HOST = '127.0.0.1'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        my_port = PORT
        while True:
            try:
                s.bind((HOST, my_port))
                break
            except:
                my_port += 1

        s.listen()
        print("Server up and listening on {0}:{1}".format(HOST, PORT))

        while True: #loop forver getting the next connection
            print("waiting for the next connection")
            conn, addr = s.accept()
            print("Got a connection from {0}".format(addr))
    
            try:
                with conn:
                   process_http_request(conn)
            except Exception as e:
                print("error: {0}".format(e))

            print("done with connection from {0}".format(addr))

def process_http_request(conn):
    buff = ''
    while True:
        data = conn.recv(1024)
        if not data:
            break
        buff += data.decode('utf-8', "ignore")
        #Check if the request is complete
        if buff.endswith("\r\n\r\n"):
            break
        #request complete
    print("Request:")
    print(buff)
    response = parse_request(buff)
    if not response:
        response = respond_404('')
    print("Response:")
    print(response)
    conn.sendall( str.encode(response))

def parse_request(buff):
    #Check if it is a GET request
    if not buff.startswith('GET'):
        return False

    (method, uri, rest) = buff.split(' ', 2) #split out the method and URI

    #Find the uri on disk
    if uri.endswith('/'):
        uri += 'index.html' #deal with index pages

    filepath = os.getcwd() + uri
    print("Looking for file'{0}'".format(filepath))
    if os.path.isfile(filepath):
        #found 
        with open(filepath) as fd:
            return make_header("200 OK", fd.read())
    else:
        print("Not found!")
        return False

def respond_404(url):
    html = '''<!DOCTYPE html>
    <HTML><HEAD><TITLE>404 Not Found</TITLE></HEAD>
    <BODY>
        <H1>404 Not Found</H1>
        <p>The request URL was not found on this server.</p>
        </BODY>
        </HTML>
    '''
    return make_header("404 Not Found", html)

def make_header(reponse_code, payload):
    header = "HTTP/1.0 {0}\r\n".format(reponse_code)
    header+= "Date: {0}\r\n".format(datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S SMT'))
    header+= "Server: my_python_server\r\n"
    header+= "Content-Length: {0}\r\n".format(len(payload))
    header+= "Connection: close\r\n"
    header+= "Content-Type: text/html\r\n"
    header+= "\r\n" #last line to end response

    return header + payload

if __name__ == "__main__":
    main()
