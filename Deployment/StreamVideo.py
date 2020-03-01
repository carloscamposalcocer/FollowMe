# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

from ServiceRunner.SerialCom import Ardu

ardu = Ardu()

PAGE = """\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
<center>
<button type="button" onclick=sendForward()>Forward!</button>
</center>
<center>
<button type="button" onclick=sendLeft()>Left!</button>
<button type="button" onclick=sendStop()>Stop!</button>
<button type="button" onclick=sendRight()>Right!</button>
</center>
<center>
<button type="button" onclick=sendBack()>Backward!</button>
</center>
</body>
</html>

<script>
function sendForward()
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
function sendBack()
{
  var xhr = new XMLHttpRequest();
  var url = "back";
  xhr.open("Get", url, true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.send();
}
function sendLeft()
{
  var xhr = new XMLHttpRequest();
  var url = "left";
  xhr.open("Get", url, true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.send();
}
function sendRight()
{
  var xhr = new XMLHttpRequest();
  var url = "right";
  xhr.open("Get", url, true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.send();
}
</script>
</html>


"""

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
        print(self.path)
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            self.send_main()
        elif self.path == "/stop":
            ardu.send(0, 0)
            self.send_main()
        elif self.path == "/start":
            ardu.send(-100, -100)
            self.send_main()
        elif self.path == "/back":
            ardu.send(100, 100)
            self.send_main()
        elif self.path == "/left":
            ardu.send(-100, -40)
            self.send_main()
        elif self.path == "/right":
            ardu.send(-40, -100)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

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


with picamera.PiCamera(resolution='320x240', framerate=24) as camera:
    output = StreamingOutput()
    # Uncomment the next line to change your Pi's Camera rotation (in degrees)
    # camera.rotation = 90
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
