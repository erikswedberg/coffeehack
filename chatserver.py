'''

Simple socket server for communicating with the iOS device managing the MetaWear.

Needs to be launched with system Python install (2.7.5), like this:

/usr/bin/python chatserver.py

To connect to this server from telnet, use:

telnet 10.90.2.142 8008

'''

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

portNum = 8008


class IphoneChat(Protocol):
    def connectionMade(self):
        #self.transport.write("""connected""")
        self.factory.clients.append(self)
        print "clients are ", self.factory.clients
    
    def connectionLost(self, reason):
        self.factory.clients.remove(self)
    
    def dataReceived(self, data):
        print "data is ", data
        a = data.split(':')
        if len(a) > 1:
            command = a[0]
            content = a[1]
            
            msg = ""
            if command == "iam":
                self.name = content
                #msg = self.name + " has joined"
                print self.name + " has joined"
            elif command == "msg":
                msg = self.name + " said " + content
            elif command == "temp":
                print "temp is "+content
            elif command == "move":
                print "move is "+content
            elif command == "b":
                msg = "bright: " + content
            elif command == "h":
                msg = "hue: " + content
            elif command == "s":
                msg = "saturation: " + content
            elif command == "low":
                msg = "lowTemp: " + content
            elif command == "high":
                msg = "highTemp: " + content
            elif command == "poll":
                msg = "pollTemp: " + content
            elif command == "t":
                msg = "setTemp: " + content
            elif command == "g":
                msg = "getTemp:0"
            elif command == "u":
                msg = "updateStrand:0"
            elif command == "r":
                msg = "resetStrand:0"
            else:
                print content
                print command
            
            print msg
                        
            for c in self.factory.clients:
                c.message(msg)
                
    def message(self, message):
        self.transport.write(message + '\n')

factory = Factory()
factory.protocol = IphoneChat
factory.clients = []

reactor.listenTCP(portNum, factory)
print "Chat server started"
reactor.run()

