import http.server
import urllib
import traceback
import sys

class DummyHandler(http.server.BaseHTTPRequestHandler):

    parser=None #A global variable having an instance of a parser which has a .parse_text(txt) method, set by whoever uses this

    def process(self,txt):
        try:
            resp=self.parser.parse_text(txt)
        except:
            self.send_response(500,"Internal server error")
            self.end_headers()
            self.wfile.write(traceback.format_exc().encode("utf-8"))
            self.wfile.flush()
            self.close_connection=True
            return

        self.send_response(200, 'OK')
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(resp.encode("utf-8"))
        self.wfile.flush()
        self.close_connection=True
            
    
    def do_GET(self):
        try:
            data=urllib.parse.urlparse(self.path)
            txt=urllib.parse.parse_qs(data.query)["text"][0]
        except:
            self.send_response(400, 'Bad request, missing ?text=txt')
            self.end_headers()
            self.close_connection=True
            return
        self.process(txt)
            
        

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            txt=self.rfile.read(content_length).decode("utf-8")
            sys.stderr.flush()
        except:
            self.send_response(400, 'Bad request')
            self.end_headers()
            self.wfile.write(traceback.format_exc().encode("utf-8"))
            self.close_connection=True
            return
        self.process(txt)
