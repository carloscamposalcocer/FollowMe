import logging
import io
import socketserver
from threading import Condition
from http import server
from ServiceRunner.ServiceRun import Service

logging.basicConfig(filename="/home/pi/Documents/FollowMe/Deployment/FollowMe.log",
                    level=logging.DEBUG,
                    format='%(asctime)s-%(name)s-%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)
logger.info("Init Main logger")

PAGE = """\
<html>
<head>
<title>MyPetBot</title>
</head>
<body>
<center><h1>MyPetBot</h1></center>
<center><button type="button" onclick=sendStart()>Start!</button></center>
<center><button type="button" onclick=sendStop()>Stop!</button></center>
</body>
</html>

<script>
function sendStart()
{
  var xhr = new XMLHttpRequest();
  var url = "start";
  xhr.open("Get", url, true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.send();
}
function sendStop()
{
  var xhr = new XMLHttpRequest();
  var url = "stop";
  xhr.open("Get", url, true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.send();
}
</script>
</html>


"""
service = Service()


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            self.send_main()
        elif self.path == "/stop":
            service.stop()
            self.send_main()
        elif self.path == "/start":
            service.start()
            self.send_main()

    def send_main(self):
        content = PAGE.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


address = ('', 8000)
server = StreamingServer(address, StreamingHandler)

logger.info("Starting Web Service")
server.serve_forever()
logger.info("Exiting Web Service")
