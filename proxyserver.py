##########################################################
# This RNS example demonstrates how to set up a link to  #
# a destination, and pass binary data over it using a    #
# channel buffer.                                        #
##########################################################
from __future__ import annotations
import os
import sys
import time
import argparse
from datetime import datetime
import RNS
from RNS.vendor import umsgpack
import ignition
import urllib.parse
APP_NAME = "Gemini_Proxy"

##########################################################
#### Server Part #########################################
##########################################################

#self.identity_file = identity_file
# This initialisation is executed when the users chooses
# to run as a server
def server(configpath):
    
    # Randomly create a new identity for our link example
    identity_file = "proxy_server_identity"

    # We must first initialise Reticulum
    reticulum = RNS.Reticulum(configpath)
 
    if RNS.Identity.from_file(identity_file):
        server_identity = RNS.Identity.from_file(identity_file)
        print(f"Loaded existing identity from {identity_file}")
    else:
        server_identity = RNS.Identity()
        server_identity.to_file(identity_file)
        print(f"Created new identity and saved to {identity_file}")


    # We create a destination that clients can connect to. We
    # want clients to create links to this destination, so we
    # need to create a "single" destination type.
    server_destination = RNS.Destination(
        server_identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        APP_NAME,
        "resourceproxy"
    )

    # We configure a function that will get called every time
    # a new client creates a link to this destination.
    server_destination.set_link_established_callback(client_connected)

    # Everything's ready!
    # Let's Wait for client resources or user input
    server_loop(server_destination)


def server_loop(destination):
    # Let the user know that everything is ready
    RNS.log(
        "Resource example "+
        RNS.prettyhexrep(destination.hash)+
        " running, waiting for a connection."
    )

    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")

    # We enter a loop that runs until the users exits.
    # If the user hits enter, we will announce our server
    # destination on the network, which will let clients
    # know how to create messages directed towards it.
    while True:
        entered = input()
        destination.announce()
        RNS.log("Sent announce from "+RNS.prettyhexrep(destination.hash))

# When a client establishes a link to our server
# destination, this function will be called with
# a reference to the link.

def client_connected(link):

    RNS.log("Client connected")

    # We configure the link to accept all resources
    # and set a callback for completed resources
    link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
    link.set_resource_concluded_callback(resource_concluded)

    link.set_link_closed_callback(client_disconnected)

def resource_concluded_sending(resource):
    if resource.status == RNS.Resource.COMPLETE: 
        RNS.log(f"The resource {resource} was sent successfully")
        
    else: 
        RNS.log(f"Sending the resource {resource} failed")

def client_disconnected(link):
    RNS.log("Client disconnected")

def resource_concluded(resource):

    print (resource.link)
    if resource.status == RNS.Resource.COMPLETE:
        RNS.log(f"Metadata: {resource.metadata}")
        RNS.log(f"Data length: {os.stat(resource.data.name).st_size}")
        udata = resource.data.read()
        RNS.log(f"First 32 bytes of data: {udata}")
        data = udata.decode('utf-8')
        certset = ('certP.pem','keyP.pem')  # filename and folder of the certificated to your Gemini authentification 
        response = ignition.request("gemini://"+str(data),ca_cert=certset) # private server with cert
        #response = ignition.request("gemini://"+data) 
        parsed =  urllib.parse.urlparse("gemini://"+data)

        master_scheme = parsed.scheme
        master_netloc = parsed.netloc
        master_spath1 = parsed.path
        master_spath = master_spath1.split("/" or "\n")

        if response.is_a(ignition.SuccessResponse):
            
            msg_final = response.data()
            metadata = response.meta
            print (metadata)
            RNS.log("Received data from " + data)

            reply_message = msg_final
            
             
        elif response.is_a(ignition.InputResponse):
            reply_message = '10 input %s \r\n' % (response.data())
            
                
            print(f"Needs additional input: {response.data()}")

        elif response.is_a(ignition.RedirectResponse):
            data = response.data()
            #print (data+"----"+master_netloc)
            response = ignition.request(data,referer="gemini://"+master_netloc,ca_cert=certset) # Private
#            response = ignition.request(data,referer="gemini://"+master_netloc) # Public

            reply_message ='20 %s' % (response.data())
            print(f"Received response, redirect to: {response.data()}")
            
        elif response.is_a(ignition.TempFailureResponse):
            reply_message ='Error from server: %s' % (response.data())

            print(f"Error from server: {response.data()}")
            
        elif response.is_a(ignition.PermFailureResponse):
            reply_message ='Error from server: %s' % (response.data())

            print(f"Error from server: {response.data()}")
            
        elif response.is_a(ignition.ClientCertRequiredResponse):
            reply_message ='60 %s' % (response.data()) 
            print(f"Client certificate required. {response.data()}")
            
        elif response.is_a(ignition.ErrorResponse):
            reply_message ='%s' % (response.data().encode("utf-8"))
            print(f"There was an error on the request: {response.data()}")
            
        else:
            RNS.log(f"Receiving resource {resource} failed")

        metadata = response.meta
        if type(reply_message) == str : 
            reply_message = reply_message.encode('utf-8')
        # Send the resource
        resource = RNS.Resource(reply_message, resource.link, metadata=metadata, callback=resource_concluded_sending, auto_compress=True)
#        resource = RNS.Resource(reply_message, resource.link, metadata=metadata, auto_compress=True)
##########################################################
#### Program Startup #####################################
##########################################################

# This part of the program runs at startup,
# and parses input of from the user, and then
# starts up the desired program mode.
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple buffer example")

        parser.add_argument(
            "-s",
            "--server",
            action="store_true",
            help="wait for incoming link requests from clients"
        )

        parser.add_argument(
            "--config",
            action="store",
            default=None,
            help="path to alternative Reticulum config directory",
            type=str
        )

        args = parser.parse_args()
        if args.config:
            configarg = args.config
        else:
            configarg = None

        server(configarg)

    except KeyboardInterrupt:
        print("")
        sys.exit(0)

