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
import zlib
import RNS
from RNS.vendor import umsgpack
import ignition
APP_NAME = "Gemini_Proxy"


##########################################################
#### Server Part #########################################
##########################################################

# A reference to the latest client link that connected
latest_client_link = None

# A reference to the latest buffer object
latest_buffer = None
#self.identity_file = identity_file
# This initialisation is executed when the users chooses
# to run as a server
def server(configpath):

    # Let's define an app name. We'll use this for all
    # destinations we create. Since this echo example
    # is part of a range of example utilities, we'll put
    # them all within the app namespace "example_utilities"
 
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
        APP_NAME
        )

    # We configure a function that will get called every time
    # a new client creates a link to this destination.
    server_destination.set_link_established_callback(client_connected)

    # Everything's ready!
    # Let's Wait for client requests or user input
    server_loop(server_destination)

def server_loop(destination):
    global latest_buffer
    buffer = latest_buffer
    # Let the user know that everything is ready
    RNS.log(
        "Link buffer example "+
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
    global latest_client_link, latest_buffer
    latest_client_link = link

    RNS.log("Client connected")
    link.set_link_closed_callback(client_disconnected)

    # If a new connection is received, the old reader
    # needs to be disconnected.
    if latest_buffer:
        latest_buffer.close()


    # Create buffer objects.
    #   The stream_id parameter to these functions is
    #   a bit like a file descriptor, except that it
    #   is unique to the *receiver*.
    #
    #   In this example, both the reader and the writer
    #   use stream_id = 0, but there are actually two
    #   separate unidirectional streams flowing in
    #   opposite directions.
    #
    channel = link.get_channel()
    latest_buffer = RNS.Buffer.create_bidirectional_buffer(0, 0, channel, server_buffer_ready)

def client_disconnected(link):
    RNS.log("Client disconnected")

def server_buffer_ready(ready_bytes: int):
    """
    Callback from buffer when buffer has data available

    :param ready_bytes: The number of bytes ready to read
    """
    global latest_buffer

    data = latest_buffer.read(ready_bytes)
    data = data.decode("utf-8")
    print ("--+> "+data)
    #certset = ('cert1.pem','key1.pem')  # filename and folder of the certificated to your Gemini authentification 
    #response = ignition.request("gemini://"+str(data),ca_cert=certset) # private server with cert
    response = ignition.request("gemini://"+str(data)) # for Public server
    if response.is_a(ignition.SuccessResponse):
        print (response.meta[:11])
        msg_final = response.data()
        
        RNS.log("Received data over the buffer: " + data)

        reply_message = msg_final
        if response.meta[:5] == 'text/' :
            reply_message = zlib.compress(reply_message.encode("utf-8"),9)nomadnet
        
        latest_buffer.write(reply_message)
        #latest_buffer.write("<<EOF>>".encode("utf-8"))
        
    elif response.is_a(ignition.InputResponse):
        reply_message = '10 input %s \r\n' % (response.data())
        latest_buffer.write(reply_message.encode("utf-8"))
            
        print(f"Needs additional input: {response.data()}")

    elif response.is_a(ignition.RedirectResponse):
        reply_message ='30 %s' % (response.data())

        print(f"Received response, redirect to: {response.data()}")
        latest_buffer.write(reply_message.encode("utf-8"))
    elif response.is_a(ignition.TempFailureResponse):
        reply_message ='Error from server: %s' % (response.data())

        print(f"Error from server: {response.data()}")
        latest_buffer.write(reply_message.encode("utf-8"))
    elif response.is_a(ignition.PermFailureResponse):
        reply_message ='Error from server: %s' % (response.data())

        print(f"Error from server: {response.data()}")
        latest_buffer.write(reply_message.encode("utf-8"))
    elif response.is_a(ignition.ClientCertRequiredResponse):
        reply_message ='60 %s' % (response.data()) 
        print(f"Client certificate required. {response.data()}")
        latest_buffer.write(reply_message.encode("utf-8"))
    elif response.is_a(ignition.ErrorResponse):
        reply_message ='%s' % (response.data().encode("utf-8"))
        print(f"There was an error on the request: {response.data()}")
        latest_buffer.write(reply_message.encode("utf-8"))
    latest_buffer.write("<<EOF>>".encode("utf-8"))
    latest_buffer.flush()
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


