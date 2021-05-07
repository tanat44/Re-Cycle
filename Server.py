from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.parse import urlparse, parse_qs
from threading import Thread

hostName = "192.168.1.41"
serverPort = 8080

def ServerFactory(callbackValue):
    class Server(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.callbackValue = callbackValue
            super().__init__(*args, **kwargs)

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            query = urlparse(self.path).query
            query = parse_qs(query)
            value = query['value'][0]
            self.wfile.write(bytes("okok", "utf8"))
            self.callbackValue(value)

    return Server


class ServerRunner():
    def __init__(self, callbackValue):
        self.callbackValue = callbackValue
        NewServer = ServerFactory(callbackValue)
        self.webServer = HTTPServer((hostName, serverPort), NewServer)
        print("Server started http://%s:%s" % (hostName, serverPort))
        self.thread = Thread(target=self.runServer, args=())
        self.thread.start()

    def stopServer(self):
        print("Server stopped.")
        self.webServer.server_close()
        self.thread.join()

    def runServer(self):
        try:
            self.webServer.serve_forever()
        except Exception as e:
            pass


    