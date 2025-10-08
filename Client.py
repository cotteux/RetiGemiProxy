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
import zlib
from pathlib import Path
import chardet
image=""

import time
from datetime import datetime

import RNS
from RNS.vendor import umsgpack
ALLDATA = b''

required_stamp_cost = 8
enforce_stamps = False
# Let's define an app name. We'll use this for all
# destinations we create. Since this echo example
# is part of a range of example utilities, we'll put
# them all within the app namespace "example_utilities"
APP_NAME = "Gemini_Proxy"

# os.system('cls||clear')
#parser = argparse.ArgumentParser(description="Gateway to Gemini Network")
#parser.add_argument("--port", type=str, help="Specify the serial port")

#args = parser.parse_args()

page = []
total = 0
lines = 5
url = ""
murl = ""
t0 = time.time()
t1 = time.time()
jumpline = []
resend = 0
inputrequired = 0
redirect = 0
retour = ""
size = 0
message_string = ""
state = 0

try:
    import chardet
    _HAS_CHARDET = True
except ImportError:
    _HAS_CHARDET = False

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
            print('autre-----')
            filename = "cache/"+self.request_netloc+self.request_path+filequery
            url=self.request_netloc+self.request_path+urlquery
            print(url+' --  '+filename)
            #self.send_message(url)
            #self.handle_binary(filename)
        print (filename)
        
               
        # Handle what we received based on item type
        self.send_message(url)

        #self.handle_binary(filename)
        self.handle_text(filename)
        # Clean up
        self.request.close()
        #os.unlink(filename)

    def send_gemini_header(self, status, meta):
        global state
        """
        Send a Gemini header, and close the connection if the status code does
        not indicate success.
        """
        #print ("\a")
       
            
        
        if status == 21 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            time.sleep(1)
            self.request.send("The Page is loading, Be patient !!!\r\n=> gemini://{} At BEEP Click here\r\n".format(url).encode("UTF-8"))
            #self.request.send("Page size {} lines \r\n".format(lines).encode("UTF-8"))
            #self.request.send("at speed of 15 to 40 bytes/sec on Longfast Channel\r\n".format(url).encode("UTF-8"))
        elif status == 22 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            self.request.send("The Page is Too Big, more than 100 lines\r\n".format(url).encode("UTF-8"))
        elif state == 10 :
            print("OOOK")
            self.request.send("{} {}\r\n".format(10, "input requirement").encode("UTF-8"))
            #time.sleep(1)
            #self.request.send("The Page is loading, Be patient !!!\r\n=> gemini://{} At BEEP Click here\r\n".format(url).encode("UTF-8"))
            #self.request.send("Page size {} lines \r\n".format(lines).encode("UTF-8"))
            #self.request.send("at speed of 15 to 40 bytes/sec on Longfast Channel++\r\n".format(url).encode("UTF-8"))    
        else : 
            self.request.send("{} {}\r\n".format(status, meta).encode("UTF-8"))    
            #print ("{} {}\r\n".format(status, meta))
            #print ("envoie autre status "+str(state))
        #if status / 10 != 2:
        #    self.request.close()
        
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
        #print ("----> "+ self.request_netloc)
        #print (parsed)
        
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
        #print ("*-0 "+mimetype)
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
        global url,murl,retour,resend,t0,t1,message_string,ALLDATA
        load = 0
        t0 = time.time()  
        #print ("/////"+mime)
        """
        Send a Gemini response with a given MIME type whose body is the
        contents of the specified file.
        """

        while ALLDATA[-7:] != b"<<EOF>>":       
            time.sleep(0.2)
            
        if ALLDATA !=b'' :
            #print (ALLDATA)   
            mread = ALLDATA[:-7]
            try :
                readd = mread.decode('utf-8')
            except :
                print ("++"+self.request_path[-4:])
                if '.jpg'  in self.request_path or '.JPG'  in self.request_path :                
                    mime='image/jpg'                
                elif '.png' in self.request_path  :                
                    mime='image/png'                
                elif '.gif' in self.request_path  :                
                    mime='image/gif'                
                else :
                    mime='application/octet-stream'
                
                readd = '20'

                
            readcode = readd[:2]
            #print("->> "+readd)
            if readcode == "10" : 
                self.send_gemini_header(10,readd[2:])
                #self.request.send(mread[2:])
                print("input")                    
            elif readcode == "30" : 
                url = readd[3:]
                self.send_gemini_header(30,url)
#                            self.request.send(url)                        
                #print(url)
            elif readcode == "60" : 
                self.send_gemini_header(60,readd[2:])

            else:
                self.send_gemini_header(20, mime)
                self.request.send(mread)  


            ALLDATA = b''
           
            retour = ""
                
        else:
            print('This file doesn\'t exist. Load from Gemini')
            
            self.send_message(url)
            
            
             
            
            #self.send_gemini_header(23,"text/gemini")
            
            
            x=0
            #print (" LOADING...")
            
            #print (ALLDATA)                   
               

            

            mread = ALLDATA
            readd = mread.decode('utf-8')
            readcode = readd[:2]
            #print("->> "+readd)
            if readcode == "10" : 
                self.send_gemini_header(10,readd[2:])
                #self.request.send(mread[2:])
                print("input")
            elif readcode == "30" : 

                url = readd[3:]
                self.send_gemini_header(30,url)
#                            self.request.send(url)
                
                #print(url)
            elif readcode == "60" : 
                self.send_gemini_header(60,readd[2:])

            else:
                self.send_gemini_header(20, mime)

                self.request.send(mread)                        
            #self.request.send(fp.read())

                
            retour = ""
            t1 = time.time()
            ALLDATA = b''




    def send_message(self,text) :
        global server_link,t0
        # Wait for the link to become active
        while not server_link:
            time.sleep(0.1)

        should_quit = False
        text = text.encode("utf-8")
        buffer.write(text)
        # Flush the buffer to force the data to be sent.
        buffer.flush()
        t0 = time.time() 

# When the buffer has new data, read it and write it to the terminal.
def client_buffer_ready(ready_bytes: int):
    global retour,url,state,t0,t1,ALLDATA
     
    retour = ""
    global buffer,message_string
    
    #os.system('cls||clear')
    
    
            
    try:
        global buffer
        ddata = ""
        data = buffer.read(ready_bytes)
        t1 = time.time()
        t0t1 = t1-t0
        print ("%.2f seconds passed %.0f bytes received total"%(t0t1,len(ALLDATA)+len(data)))
       
        if data != None : 
            ddata = data
        if ddata[-7:] != b"<<EOF>>" :
            if ddata != "":
                
                if ddata[:8] =="10 input"   :
                    
                    print ("input required whouwhou")
                    retour = "10 "+ddata[9:]
                    state = 10
                    
                elif ddata[:12] =="redirect to:"   :
                    url = ddata[13:]
                    #self.send_gemini_header(20, url)
                    print ("redirect-------- "+url)
                    state = 20
                    retour = "30 "+url

                elif ddata[:28] =="Client certificate required."   :
                    url = ddata[13:]
                    #self.send_gemini_header(60, url)
                    print ("certificate needed")
                    state = 60
                  
                    retour = "60 "+"cert"
                elif ddata[:9] =="Not Found" or ddata[:12] =="Unknown host" or ddata[:18] =="Connection refused" or ddata[:14] =="Socket timeout" or ddata[:17] =="Error from server":
                    url = ddata[13:]
                    #self.send_gemini_header(20, url)
                    print ("server not found")
                    retour = "50 "+"NO SERVER"
                
                                     
       
                else :
                    retour = ""
                    #message_string = message_string + ddata
                    
                    ALLDATA = ALLDATA + data
                    #print (ALLDATA)
                    #print(data)
                    #print ('---------------------')
                    
        else :
            #message_string = message_string + ddata
            #print("************************ " )
            #ALLDATA = message_string
            #print (data[:-7])
            sizec =  len(ALLDATA+data)
            ALLDATA = ALLDATA + data[:-7]            
            try :            
                ALLDATA = zlib.decompress(ALLDATA)+b"<<EOF>>"
            except:
                ALLDATA = ALLDATA+b"<<EOF>>"
            t1 = time.time()
            t0t1 = t1-t0
            size =  len(ALLDATA)
            #print('\a')
            #print('\007')
            #print ("t0   %f secondes"% t0)
            #print (ALLDATA)
            print (sizec)
            print ("("+str(sizec)+"C) "+str(size)+" bytes in %.2f secondes "% t0t1+str(int(sizec/t0t1*8))+" bauds real")
            print ("Received speed "+str(int(size/t0t1))+" bytes/second also "+str(int(size/t0t1*8))+" bauds compress")
            sys.stdout.flush()
            page.clear()
            jumpline.clear()
            total = 0
            lines = 0
            resend = 0
            message_string = ""

       
    except KeyError as e:
        print(f"Error processing packet: {e}")




##########################################################
#### Client Part #########################################
##########################################################

# A reference to the server link
server_link = None

# A reference to the buffer object, needed to share the
# object from the link connected callback to the client
# loop.
buffer = None

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
        APP_NAME    
    )

    # And create a link
    link = RNS.Link(server_destination)

    # We'll also set up functions to inform the
    # user when the link is established or closed
    link.set_link_established_callback(link_established)
    link.set_link_closed_callback(link_closed)

    # Everything is set up, so let's enter a loop
    # for the user to interact with the example
    #client_loop()

def client_loop():   # send data ****
    global server_link

    # Wait for the link to become active
    while not server_link:
        time.sleep(0.1)

    should_quit = False
    while not should_quit:
        try:
            #print("> ", end=" ")
            #text = input()
            text = ''
            # Check if we should quit the example
            if text == "quit" or text == "q" or text == "exit":
                should_quit = True
                server_link.teardown()
            else:
                # Otherwise, encode the text and write it to the buffer.
                text = text.encode("utf-8")
                buffer.write(text)
                # Flush the buffer to force the data to be sent.
                buffer.flush()


        except Exception as e:
            RNS.log("Error while sending data over the link buffer: "+str(e))
            should_quit = True
            server_link.teardown()

# This function is called when a link
# has been established with the server
def link_established(link):
    # We store a reference to the link
    # instance for later use
    global server_link, buffer
    server_link = link

    # Create buffer, see server_client_connected() for
    # more detail about setting up the buffer.
    channel = link.get_channel()
    buffer = RNS.Buffer.create_bidirectional_buffer(0, 0, channel, client_buffer_ready)

    # Inform the user that the server is
    # connected
    RNS.log("Link established with server, enter some text to send, or \"quit\" to quit")

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




#recipient_hexhash = "33d04ec7f146a4411b3f874c6fce0151"
recipient_hexhash = "45719d253b983a37a1c61aa54c9679cb"  # public server without Gemini authentification certificated


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


