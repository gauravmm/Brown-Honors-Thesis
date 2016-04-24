# This connects a webpage to the thingy.

import SimpleHTTPServer
import SocketServer
import urllib;
from incrementalParser import IncrementalParser;

execfile("./params.py");

scenes = load_scenes();
sc = scenes['8'];

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, *args):
        self.ip = None;
        return SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args);
    
    def do_GET(self):
        data = None;
        reset = False;
        if self.path[0:4] == "/new":
            print "NEW"
            data = self.path[4+5:];
            reset = True;
        elif self.path[0:7] == "/update":
            data = self.path[7+5:];            
        else:
            if self.path == '/':
                self.path = '/interface.html';
            
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self);
        
        # Since we are here, we need to process the string in data.
        
        data = urllib.unquote(data).strip().split();
        print data;
        if reset or not self.ip:
            if self.ip:
                self.ip.close();
            self.ip = IncrementalParser(sc);
        
        dist = self.ip.setTo(data);
        sendstr = ", ".join(str(ob) + ": " + str(dist["orange_" + str(ob)]) for ob in range(1, 8) if "orange_" + str(ob) in sc)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        
        self.wfile.write(sendstr);
        self.wfile.close();


Handler = MyRequestHandler
server = SocketServer.TCPServer(('0.0.0.0', 8888), Handler);

try:
    server.serve_forever()
finally:
    server.server_close();