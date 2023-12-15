# ________________________________________________________ TimerCheck CP900a6 http-server server.poll
import os
import time  # ___________________________________________ we use time.monotonic aka seconds in float
import gc # micropython garbage collection # use gc.mem_free() # use gc.collect()
from adafruit_datetime import  datetime
import rtc
import adafruit_ntp # V1.0.2 b use NTP time to set PICO W RTC
import socketpool
from ipaddress import ip_address
import wifi
from adafruit_httpserver import Server, Request, Response, Redirect, GET, POST
import micropython
import microcontroller # for board reboot

DIAG = True # False # ___________________________________ global print disable switch / overwritten by console [D][enter]
DIAG = bool(os.getenv('DIAG')) # ______________________________ now get from settings.toml

def dp(line=" ", ende="\n"):
    if DIAG : print(line, end=ende)

def check_mem(info="",prints=True,coll=True) :
    if prints :
        dp("\n___ {:} check mem   : {:}".format( info, gc.mem_free()) )
    if coll :
        gc.collect()
    if ( prints and coll ) :
        dp("___ after clear : {:}".format( gc.mem_free()) )

# call:     check_mem(info = " JOBx after y",prints=True,coll=True)

THIS_REVISION = os.getenv('THIS_REVISION')
THIS_OS = os.getenv('THIS_OS')

WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')

WIFI_IP = os.getenv('WIFI_IP')

TZ_OFFSET = os.getenv('TZ_OFFSET') # for NTP to RTC
useNTP = os.getenv('useNTP')

def get_network_time():
    if ( useNTP == 1 ) :
        try:
            print("___ get NTP to RTC")
            ntp = adafruit_ntp.NTP(pool, tz_offset=TZ_OFFSET)
            rtc.RTC().datetime = ntp.datetime # NOTE: This changes the system time
        except:
            print("failed")

def show_time(lDIAG=True):
    if  (useNTP == 1 ) :
        #print(time.localtime())
        tnow = datetime.now()
        tnows = tnow.isoformat()
        tnows = tnows.replace("T"," ")
        if lDIAG:
            dp(tnows)
        return tnows
    else :
        return " "




# ______________________________ at the HTML STYLE section i had to escape the { , } by {{ , }}
HTML_INDEX = """
<!DOCTYPE html><html><head>
<title>KLL engineering Pico W</title>
<link rel="icon" type="image/x-icon" href="favicon.ico">
<style>
body {{font-family: "Times New Roman", Times, serif; background-color: lightgreen;
display:inline-block; margin: 0px auto; text-align: center;}}
h1 {{color: deeppink; word-wrap: break-word; padding: 1vh; font-size: 30px;}}
p {{font-size: 1.5rem; word-wrap: break-word;}}
p.dotted {{margin: auto; width: 75%; font-size: 25px; text-align: center;}}
form {{font-size: 2rem; }}
input[type=number] {{font-size: 2rem;}}
</style>
<meta http-equiv="refresh" content="5">
</head><body>
<h1>Pico W Web Server from Circuit Python {THIS_OS} </h1>
<img src="https://www.raspberrypi.com/documentation/microcontrollers/images/picow-pinout.svg" >
<hr>
<table style="width:100%">
<tr>
<th>
<p><a href="http://kll.byethost7.com/kllfusion01/infusions/articles/articles.php?article_id=225" target="_blank" >
<b>kll engineering blog</b></a></p>
</th>
<th>
<p>rev: {THIS_REVISION}</p>
</th>
</tr>
</table>
<p> auto refresh 5 sec to see some load for server </p>
<hr>
</body></html>
"""

def setup_webserver() :
    global server, pool
    dp("\n\nwww PICO W: Hello World! start webserver (STA)\n")
    dp("www Connecting to router {:s} OR CHECK THE 'settings.toml' FILE".format( WIFI_SSID) )
    wifi.radio.set_ipv4_address( # _______________________ fixIP ( requires > CP 8.0.0 beta 4 )
        ipv4=ip_address(WIFI_IP),
        netmask=ip_address("255.0.0.0"),
        gateway=ip_address("192.168.1.1"),
        ipv4_dns=ip_address("192.168.1.1"),
    )
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    dp("www Connected to {:s}".format( WIFI_SSID) )
    dp("www Listening on http://{:s}:80 ".format(str(wifi.radio.ipv4_address)) )

    pool = socketpool.SocketPool(wifi.radio)

    get_network_time() # _________________________________ get network time to RTC
    show_time()

    # ____________________________________________________ make a WEB SERVER
    server = Server(pool, "/static") #, debug=True)

    @server.route("/")
    def base(request):  # pylint: disable=unused-argument
        dp("\nwww served dynamic index.html")
        check_mem(info = "serve /",prints=False,coll=True)
        return Response(request,
            HTML_INDEX.format(
                THIS_OS=THIS_OS,
                THIS_REVISION=THIS_REVISION,
                ),
                content_type='text/html'
            )
    server.start(str(wifi.radio.ipv4_address)) # _________ startup the server

def run_webserver() :
    global server
    try:
        server.poll()

    except OSError:
        print("ERROR server poll")
        # _________________________________________________ here do a reboot
        microcontroller.reset()


setup_webserver()  # _____________________________________ start wifi and NTP and webserver



# ________________________________________________________ we run a Mloop counter and check at 1 000 000
Mloop_s = time.monotonic()
last_Mloop_s = time.monotonic()
loopM = 0
updateM = 1000000
secdotprint = True
# ________________________________________________________ we run a loop1 counter and check at 1 sec
start_s1 = time.monotonic()
loop1 = 0
loopt1 = 10  # _________________________________________ we can read time every loop OR every loopt loop only, makes the 1M faster/ but timer more inaccurate
update1 = 1.0  # _________________________________________ every 1 sec do


while True:  # ___________________________________________ MAIN
    try:
        loopM += 1
        if ( loopM >= updateM ):  # ______________________ 1 million loop timer / reporter
            loopM = 0
            Mloop_s = time.monotonic()
            dp("\n___ 1Mloop: {:>5.3f} sec ".format((Mloop_s - last_Mloop_s)))
            last_Mloop_s = Mloop_s  # ____________________ remember
            check_mem(info = "loopM",prints=True,coll=True)

        loop1 += 1
        if loop1 > loopt1:
            loop1 = 0
            now_s1 = time.monotonic()  # _______________ JOB1 is a timed job, but use a counter to NOT read millis every loop as that's slow
            next_s1 = start_s1 + update1
            if now_s1 >= next_s1:  # _______ 1 sec
                if secdotprint:
                    dp(
                        ".", ""
                    )  # _______________________ means print(".",end="") aka NO LINEFEED, but makes it difficult to scroll the REPL UP
                start_s1 += 1.0
                # here a 1 sec job

                check_mem(info = "loop1 prior run_webserver",prints=False,coll=True)
                run_webserver()  # __________________________________ in main loop it's killing me, better in 1 sec loop
                check_mem(info = "loop1 after run_webserver",prints=False,coll=True)

        #run_webserver()  # __________________________________ in main loop it's killing me, better in 1 sec loop

    except OSError:
        microcontroller.reset()



'''
1Mloop only
9.8 sec mem: 47952 mem low: 45072

1Mloop and loop1
18.0 sec mem:47800 mem low: 45206

1Mloop and loop1 run_webserver
18.7 sec mem: 47600 memlow: 47584

1Mloop and loop1 run_webserver and webpage / autorefresh 5 sec
21.4 sec mem: 52320 memlow: 47584

need change loopt1 from 1000 to 10 to have a 1 sec tick
run_webserver in main loop ( delete 2 front [tab] )
1Mloop and loop1
226.1 sec mem: 52480 mem low: 18912

start webpage / autorefresh 5 sec but sometimes need 20 sec?
233.4 sec mem: 52480 mem low: 27872

'''
