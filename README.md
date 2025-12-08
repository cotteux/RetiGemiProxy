# RetiGemiProxy
Gemini proxy for using Lagrange with Lora network on Reticulum Network
PROTOTYPE WIP

This program connect your Lagrange browser (or any Gemini Browser with a proxy option) through Reticulum Network to connect at Gemini Network.
Why I did this. Want to work with Lora communication easilly using rnode to Navigate throught Gemini with all options.

## Proxy Server Private mode (Limited)
   Add only one Certificate to Authenticated on many Gemini capsule for only one user. 
   Private server need a certificate for the tls gemini connection , you need to create it with openssl like this
   
      openssl req -x509 -newkey rsa:4096 -keyout key1.pem -out cert1.pem -days 365 -nodes -subj
   
   uncomment these 2 lines in proxyserver.py
   
     #certset = ('cert1.pem','key1.pem')  # filename and folder of the certificated to your Gemini authentification you create with openssl
     #response = ignition.request("gemini://"+str(data),ca_cert=certset) # private server with cert   
   
   and comment this line
   
     #response = ignition.request("gemini://"+str(data)) # for Public server
     
## Proxy Server Public (do this for Private server)
 --Now mutiples clients can connect to the server
   Just don't change anything.
   Need to install RNS with : 

     pip install rns
   Need to install Ignition with :
   
     pip install ignition-gemini
## Client
You can use Client.py without modification to connect direct to the TEST public server without config but not for day to day use.
The cert and key, come with are for the Client.py to connect with the browser like Lagrange.
For the Client.py you need to change recipient_hexhash for you server link. 

recipient_hexhash ="776002c84b3c1177f30c80bd74497d6e"  # public server without Gemini authentification certificated

Need to install RNS with : 

    pip install rns
Don't forget to configure your browser with the proxy localhost:1965

## Video with Lagrange browser
      https://youtu.be/g3Q5FBgYjMc
      
Some code coming from the proxy Agena https://git.sr.ht/~solderpunk/agena
