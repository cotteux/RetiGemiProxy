# RetiGemiProxy
Gemini proxy for using Lagrange with Lora network on Reticulum Network
PROTOTYPE WIP

This program connect your Lagrange browser (or any Gemini Browser with a proxy option) through Reticulum Network to connect at Gemini Network.
Why I did this. Want to work with Lora communication easilly using rnode to Navigate throught Gemini with all options.

## Proxy Server Private mode (Limited)
   Add only one Certificate to Authenticated on many Gemini capsule for only one user. 
   uncomment these 2 liines in Proxyserver
   
     #certset = ('cert1.pem','key1.pem')  # filename and folder of the certificated to your Gemini authentification (not the one coming with the github, this is for agena localhost proxy)
     #response = ignition.request("gemini://"+str(data),ca_cert=certset) # private server with cert   
   
   and comment this line
     response = ignition.request("gemini://"+str(data)) # for Public server

## Proxy Server Public
   Just don't add certificate.

the cert and key, come with are for the Client.py to connect Lagrange.

for Proxyserver create one certificate for the tls gemini connection and Another (only for Private server)

You can use Client.py with key.pem and cert.pem to connect direct to the TEST public server  without config but not for day to day use.

Need to install RNS with : **pip install rns**

##TODO
* Redirect done by the server instead of the client
* multi connections, can only manage one connection at the time

