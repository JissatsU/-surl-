# -surl-
A tool that notifies when somebody visits a url on your web server or sends an ssh connection request.

REQUIREMENTS:
1. Python2.7
2.ffmpeg [sudo apt install ffmpeg]

USAGE:
1.For url notifications [sudo main.py --iface=INTERFACE --ip=YOUR_IP --url=YOUR_URL --port=SERVER_PORT(optional)]
2.For ssh notifications [sudo main.py --iface=INTERFACE --ip=YOUR_IP --ssh --port=SERVER_PORT(optional)]
