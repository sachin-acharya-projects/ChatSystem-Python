# Socket-ChatBox-Python
It is a simple chat application made using Python Programming language and ofcourse database-less. This application can be used to communicate anonymously 🤣🤣. 

It have three scripts

- Server.py
  This is a server-side of the application which handles the communications between multiple clients

- Client.py
  This is a client-side of the application which handles outgoing messages - sending messages to server which inturns sent over to other clients
 
 - Receiver.py
  This handles incoming messages - display them and probably other connection just connected (Joining of new users to chat). Without using some sort of GUI interface,
  we cannot display incoming message and taking input from user at the same time, so two script are used to handle them separately. 
  
  It future version of this application, we might be able to merge these two scripts into single script which can handle both these task independently
  
 **Package Required**
Most of the packages are built-in

````
pip install colorama
````
