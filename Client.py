#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import mimetypes
import os
import shlex
import subprocess
import socket
import socketserver
import ssl
import sys
import tempfile
import urllib.parse
from pubsub import pub
import os
import time
import json
import RNS

from pathlib import Path

import time
from datetime import datetime

import RNS
from RNS.vendor import umsgpack


recipient_hexhash ="776002c84b3c1177f30c80bd74497d6e"  # public server without Gemini authentification certificated

ALLDATA = b''

required_stamp_cost = 8
enforce_stamps = False
# Let's define an app name. We'll use this for all
# destinations we create. Since this echo example
# is part of a range of example utilities, we'll put
# them all within the app namespace "example_utilities"
APP_NAME = "Gemini_Proxy"
os.system('cls||clear')

#parser = argparse.ArgumentParser(description="Gateway to Gemini Network")
#parser.add_argument("--port", type=str, help="Specify the serial port")

#args = parser.parse_args()

url = ""
t0 = time.time()

HOST, PORT = "0.0.0.0", 1965

class AgenaHandler(socketserver.BaseRequestHandler):
    
    def setup(self):
        global sendy
        """
        Wrap socket in SSL session.
        """
        self.request = context.wrap_socket(self.request, server_side=True)

    def handle(self):
        global url, murl
        # Parse request URL, make sure it's for a Gemini resource  *************************
        self.parse_request()

        
        if self.request_query != "":
            urlquery = "?"+self.request_query
            filequery = "!!"+self.request_query
        else :
            urlquery = ""
            filequery = ""
        
        if self.request_path[-1] == "/" and self.request_query == "" :
            filename = "cache/"+self.request_netloc+self.request_path+filequery+"index.gmi"
            url=self.request_netloc+self.request_path+urlquery
            
        else :

            filename = "cache/"+self.request_netloc+self.request_path+filequery
            url=self.request_netloc+self.request_path+urlquery
            print(url+' --  '+filename)
            #self.send_message(url)
            #self.handle_binary(filename)
        print (filename)
        
               
        # Handle what we received based on item type
        self.send_message(url)

        #self.handle_binary(filename)
        sign = '+'
        while ALLDATA == b'' :
            print (sign)
            if sign == "+" : sign ="*"
            else : sign = "+"
            time.sleep(0.5)
        self.handle_text(filename)
        # Clean up
        self.request.close()
        #os.unlink(filename)

    def send_gemini_header(self, status, meta):
      
        """
        Send a Gemini header, and close the connection if the status code does
        not indicate success.
        """
        
        if status == 21 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            time.sleep(1)
            self.request.send("The Page is loading, Be patient !!!\r\n=> gemini://{} At BEEP Click here\r\n".format(url).encode("UTF-8"))
            #self.request.send("Page size {} lines \r\n".format(lines).encode("UTF-8"))
            #self.request.send("at speed of 15 to 40 bytes/sec on Longfast Channel\r\n".format(url).encode("UTF-8"))
        elif status == 22 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            self.request.send("The Page is Too Big, more than 100 lines\r\n".format(url).encode("UTF-8"))
        elif status == 10 :

            self.request.send("{} {}\r\n".format(10, "input requirement").encode("UTF-8"))
            
        else : 
            self.request.send("{} {}\r\n".format(status, meta).encode("UTF-8"))    

        if status / 10 != 2:
            self.request.close()
        
    def parse_request(self):
        """
        Read a URL from the Gemini client and parse it up into parts,
        including separating out the Gopher item type.
        """
        requested_url = self.request.recv(1024).decode("UTF-8").strip()
        if "://" not in requested_url:
            requested_url = "gemini://" + requested_url
        parsed =  urllib.parse.urlparse(requested_url)
             
        self.request_scheme = parsed.scheme
        self.request_netloc = parsed.netloc
        self.request_path = parsed.path
        self.request_query = parsed.query

        
    def handle_binary(self, filename):
        """
        Send a Gemini response for a downloaded Gopher resource whose item
        type indicates it should be a binary file.  Uses file(1) to sniff MIME
        types.
        """

        # Detect MIME type
        out = subprocess.check_output(
            shlex.split("file --brief --mime-type %s" % filename)
        )
        mimetype = out.decode("UTF-8").strip()

        self._serve_file(mimetype, filename)
    
    def handle_text(self, filename):
        """
        Send a Gemini response for a downloaded Gopher resource whose item
        type indicates it should be plain text.
        """
        
        self._serve_file("text/gemini", filename)

        
    def handle_html(self, filename):
        """
        Send a Gemini response for a downloaded Gopher resource whose item
        type indicates it should be HTML.
        """
        self._serve_file("text/html", filename)

    def _serve_file(self, mime, filename):
        global url,ALLDATA
        """
        Send a Gemini response with a given MIME type whose body is the
        contents of the specified file.
        """
        mread = ALLDATA
        try :
            readd = mread.decode('utf-8')
        except :
            print ("not utf8 "+self.request_path[-4:])
            if '.jpg'  in self.request_path or '.JPG'  in self.request_path :                
                mime='image/jpg'                
            elif '.png' in self.request_path  :                
                mime='image/png'                
            elif '.gif' in self.request_path  :                
                mime='image/gif'
            elif '.ogg' in self.request_path  :                
                mime='audio/ogg'
            else :
                mime='application/octet-stream'
            
            readd = '20'

            
        readcode = readd[:2]

        if readcode == "10" : 
            self.send_gemini_header(10,readd[2:])
        
        elif readcode == "30" : 
            url = readd[3:]
            self.send_gemini_header(30,url)

        elif readcode == "60" : 
            self.send_gemini_header(60,readd[2:])

        else:
            self.send_gemini_header(20, mime)
            self.request.send(mread)  


        ALLDATA = b''

    def send_message(self,text) :
        global server_link
        # Wait for the link to become active
        while not server_link:
            time.sleep(0.1)

        should_quit = False
        data = text.encode("utf-8")
        
        RNS.log(f" {data}")
        
        # Generate some metadata
        metadata = 'link'
        
        # Send the resource
        resource = RNS.Resource(data, server_link, metadata=metadata, auto_compress=False, callback=resource_concluded_sending, timeout=360)

        # Alternatively, you can stream data
        # directly from an open file descriptor

        # with open("/path/to/file", "rb") as data_file:
        #     resource = RNS.Resource(data_file, server_link, metadata=metadata, callback=resource_concluded_sending, auto_compress=False)


##########################################################
#### Client Part #########################################
##########################################################

# A reference to the server link
server_link = None




# This initialisation is executed when the users chooses
# to run as a client
def client(destination_hexhash, configpath):
    # We need a binary representation of the destination
    # hash that was entered on the command line
    try:
        dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH//8)*2
        if len(destination_hexhash) != dest_len:
            raise ValueError(
                "Destination length is invalid, must be {hex} hexadecimal characters ({byte} bytes).".format(hex=dest_len, byte=dest_len//2)
            )
            
        destination_hash = bytes.fromhex(destination_hexhash)
    except:
        RNS.log("Invalid destination entered. Check your input!\n")
        sys.exit(0)

    # We must first initialise Reticulum
    reticulum = RNS.Reticulum(configpath)

    # Check if we know a path to the destination
    if not RNS.Transport.has_path(destination_hash):
        RNS.log("Destination is not yet known. Requesting path and waiting for announce to arrive...")
        RNS.Transport.request_path(destination_hash)
        while not RNS.Transport.has_path(destination_hash):
            time.sleep(0.1)

    # Recall the server identity
    server_identity = RNS.Identity.recall(destination_hash)

    # Inform the user that we'll begin connecting
    RNS.log("Establishing link with server...")

    # When the server identity is known, we set
    # up a destination
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.OUT,
        RNS.Destination.SINGLE,
        APP_NAME,
        "resourceproxy"
    )

    # And create a link
    link = RNS.Link(server_destination)
    link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
    link.set_resource_concluded_callback(resource_concluded)
    # We'll set up functions to inform the
    # user when the link is established or closed
    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    # Everything is set up, so let's enter a loop
    # for the user to interact with the example

def resource_concluded_sending(resource):
    global t0,url
    if resource.status == RNS.Resource.COMPLETE: 
        RNS.log(f"The link {url} was sent successfully")
        t0 = time.time()
    else: RNS.log(f"Sending the link {url} failed")

def resource_concluded(resource):
    global t0,ALLDATA
    if resource.status == RNS.Resource.COMPLETE: 
        
        data = resource.data.read()
        
        print(resource.get_transfer_size())
        print(resource.get_data_size())
        print(resource.is_compressed())
        print(resource.get_parts())
        total = time.time() - t0
        
        print (str(round(total,2))+" sec with a speed of "+str(round(resource.get_transfer_size()/total*8,0))+" bauds")
        print ("with compression with a speed of "+str(round(resource.get_data_size()/total*8,0))+" bauds")
        ALLDATA = data

# This function is called when a link
# has been established with the server

def link_established(link):
    # We store a reference to the link
    # instance for later use
    global server_link
    server_link = link

    # Inform the user that the server is
    # connected
    RNS.log("Link established with server, hit enter to sand a resource, or type in \"quit\" to quit")

# When a link is closed, we'll inform the
# user, and exit the program
def link_closed(link):
    if link.teardown_reason == RNS.Link.TIMEOUT:
        RNS.log("The link timed out, exiting now")
    elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
        RNS.log("The link was closed by the server, exiting now")
    else:
        RNS.log("Link closed, exiting now")
    
    time.sleep(1.5)
    sys.exit(0)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
"""Agena is a simple Gemini-to-Gopher designed to be run locally to
let you seamlessly access Gopherspace from inside a Gemini client.""")
    parser.add_argument('--cert', type=str, nargs="?", default="cert.pem",
                        help='TLS certificate file.')
    parser.add_argument('--key', type=str, nargs="?", default="key.pem",
                        help='TLS private key file.')
    parser.add_argument('--port', type=str, nargs="?", default=PORT,
                        help='TCP port to serve on.')
    parser.add_argument('--host', type=str, nargs="?", default=HOST,
                        help='TCP host to serve on.')
    args = parser.parse_args()
    
    
    
    if not (os.path.exists(args.cert) and os.path.exists(args.key)):
        print("Couldn't find cert.pem and/or key.pem. :(")
        sys.exit(1)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=args.cert, keyfile=args.key)

    socketserver.TCPServer.allow_reuse_address = True
    agena = socketserver.TCPServer((args.host, 1965), AgenaHandler)
    configarg = None
   
    
    try:
        
        client(recipient_hexhash, configarg)        
        agena.serve_forever()
        
        
    except KeyboardInterrupt:
        agena.shutdown()
        agena.server_close()
        sys.exit(0)


