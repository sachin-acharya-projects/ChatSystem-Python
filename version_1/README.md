# Socket-ChatBox-Python
It is a simple chat application made using Python Programming language and of course database-less. This application can be used to communicate anonymously 🤣🤣. 

It has three scripts

- __Server.py__  
  This is a server-side of the application which handles the communications between multiple clients

- __Client.py__  
  This is a client-side of the application which handles outgoing messages - sending messages to the server which in turn sent over to other clients
 
 - __Receiver.py__  
  This handles incoming messages - displays them and probably other connections just connected (Joining of new users to chat). Without using some sort of GUI interface,
  we cannot display incoming messages and take input from users at the same time, so two scripts are used to handle them separately. 
  
  In the future version of this application, we might be able to merge these two scripts into a single script that can handle both these tasks independently
  
 **Package Required**
Most of the packages are built-in

````
pip install colorama
````

**Potential Upgrades**:
_This includes both versions of chatbox(s)_
- File sharing between Clients
- Video Communication
- Audio Communication
- UI for sign-in and sign-up
- Separate Chatroom

#### Upgraded Project
[Visit this repository](../version_2/) for a better version of `This` project in which both receiving and sending messages can be done on the same screen. Instead of running different scripts for displaying received messages and sending messages, this project displays real-time incoming messages without the need for user interaction and also allow the user to send a message from the same screen.
