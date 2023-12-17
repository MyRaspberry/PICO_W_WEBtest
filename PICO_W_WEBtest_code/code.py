#SH_T
'''
no, that is not bad talking, it is to be enabled ( remove # ) and [SAVE]
and that will lead to a RELOAD and FAIL with a error msg.
***
Traceback (most recent call last):
  File "code.py", line 1, in <module>
NameError: name 'SH_T' is not defined
***
so you can scroll up in the REPL and read and save old msg's from there
WHY THAT? well, for me the [ctrl][c] in MU-Editor REPL to stop program execution does NOT always work,
and this is my workaround: just force load broken code LOL
'''

# ________________________________________________________ TimerCheck CP900a6 http-server server.poll

import gc # micropython garbage collection # use gc.mem_free() # use gc.collect()
print(f"\nFREE MEM report after imports\n+ import gc {gc.mem_free()} ")
import os
print(f"+ import os {gc.mem_free()} ")
import time  # ___________________________________________ we use time.monotonic aka seconds in float
print(f"+ import time {gc.mem_free()} ")
from adafruit_datetime import  datetime
print(f"+ from adafruit_datetime import  datetime {gc.mem_free()} ")
import rtc
print(f"+ import rtc {gc.mem_free()} ")
import adafruit_ntp # use NTP time to set PICO W RTC
print(f"+ import adafruit_ntp {gc.mem_free()} ")
import socketpool
print(f"+ import socketpool {gc.mem_free()} ")
from ipaddress import ip_address
print(f"+ from ipaddress {gc.mem_free()} ")
import wifi
print(f"+ import wifi {gc.mem_free()} ")
from adafruit_httpserver import Server, Request, Response, Redirect, GET, POST # , Websocket
print(f"+ from adafruit_httpserver import Server, Request, Response, Redirect, GET, POST {gc.mem_free()} ")
import micropython
print(f"+ import micropython {gc.mem_free()} ")
import microcontroller # for board reboot
print(f"+ import microcontroller {gc.mem_free()} ")

# test3 async for server.poll
#import adafruit_ticks
#from asyncio import create_task, gather, run, sleep as async_sleep

DIAG = True # False # ___________________________________ global print disable switch / overwritten by console [D][enter]
DIAG = bool(os.getenv('DIAG')) # ______________________________ now get from settings.toml

def dp(line=" ", ende="\n"):
    if DIAG : print(line, end=ende)


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
        tnow = datetime.now()
        tnows = tnow.isoformat(sep=' ')
        if lDIAG:
            dp(tnows)
        return tnows
    else :
        return " "

def check_mem(timestamps=True,info="",prints=True,coll=True) :
    times=""
    if ( timestamps ) :
        times = show_time(lDIAG=False)
    if prints :
        freeold=gc.mem_free()
    if coll :
        gc.collect()
        if ( prints ) :
            dp("\n___ {0} {1} check mem   : {2} after clear : {3} ".format( times, info, freeold, gc.mem_free()) )
    else:
        if ( prints ) :
            dp("\n___ {0} {1} check mem   : {2} ".format( times, info, freeold) )

# call:     check_mem(timestamps=True,info = " JOBx after y",prints=True,coll=True)


REFRESH = 5

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
<meta http-equiv="refresh" content="{REFRESH}">
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
<p style="color:red;"> auto refresh 5 sec to see some load for server </p>
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
    server = Server(pool, "/static", debug=True)

    @server.route("/")
    def base(request):  # pylint: disable=unused-argument
        dp("\nwww served dynamic index.html")
        check_mem(info = "serve /",prints=False,coll=True)
        return Response(request,
            HTML_INDEX.format(
                THIS_OS=THIS_OS,
                THIS_REVISION=THIS_REVISION,
                REFRESH=REFRESH,
                ),
                content_type='text/html'
            )
    server.start(str(wifi.radio.ipv4_address)) # _________ startup the server

'''
async def handle_http_requests():
    while True:
        server.poll()

        await async_sleep(0)

async def handle_websocket_requests():
    while True:
        if websocket is not None:
            if (data := websocket.receive(fail_silently=True)) is not None:
                r, g, b = int(data[1:3], 16), int(data[3:5], 16), int(data[5:7], 16)
                pixel.fill((r, g, b))

        await async_sleep(0)


async def send_websocket_messages():
    while True:
        if websocket is not None:
            cpu_temp = round(microcontroller.cpu.temperature, 2)
            websocket.send_message(str(cpu_temp), fail_silently=True)

        await async_sleep(1)


async def main():
    await gather(
        create_task(handle_http_requests()),
        #create_task(handle_websocket_requests()),
        #create_task(send_websocket_messages()),
    )
'''

def run_webserver() :
    global server
    try:
        ret = server.poll()
        #dp(ret)
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
loopt1 = 1000  # _________________________________________ we can read time every loop OR every loopt loop only, makes the 1M faster/ but timer more inaccurate
update1 = 1.0  # _________________________________________ every 1 sec do


#run(main()) # ____________________________________________ async test3

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

                check_mem(timestamps=True,info = "loop1 prior run_webserver",prints=False,coll=True)
                #now_check = time.monotonic() # as server diag no help we check time here
                run_webserver()  # __________________________________ in main loop it's killing me, better in 1 sec loop
                #dp("dt: {:>7.4f} sec".format( time.monotonic() - now_check ) )
                check_mem(info = "loop1 after run_webserver",prints=False,coll=True)

        #check_mem(info = "MAIN prior run_webserver",prints=True,coll=False)
        #run_webserver()  # __________________________________ in main loop it's killing me, better in 1 sec loop

    except OSError:
        microcontroller.reset()



'''
for CP900a6:

FREE MEM report after imports
+ import gc 124048
+ import os 123920
+ import time 123840
+ from adafruit_datetime import  datetime 99232
+ import rtc 99120
+ import adafruit_ntp 98192
+ import socketpool 98112
+ from ipaddress 98000
+ import wifi 97920
+ from adafruit_httpserver import Server, Request, Response, Redirect, GET, POST 53376
+ import micropython 53216
+ import microcontroller 53088

-a-
1Mloop only
9.8 sec mem: 47952 mem low: 45072
-b-
1Mloop and loop1
18.0 sec mem:47800 mem low: 45206
-c-
1Mloop and loop1 run_webserver
18.7 sec mem: 47600 mem low: 47584
-d-
1Mloop and loop1 run_webserver and webpage / autorefresh 5 sec
21.4 sec mem: 52320 mem low: 47584

no gc.collect at run_webserver mem: 52240 mem low:46672
-e-
need change loopt1 from 1000 to 10 to have a 1 sec tick
run_webserver in main loop ( delete 2 front [tab] )
1Mloop and loop1
226.1 sec mem: 52480 mem low: 18912
-e+f-
start webpage / autorefresh 5 sec but sometimes need 20 sec?
233.4 sec mem: 52480 mem low: 27872
-e+f+g-
test mem for it without gc.collect
mem: 52160 mem low: 672 ? // mem runs down but autorecovers ?

!!! server.poll() is a timing and memory pig !!!

# _______________________
test2 deleted
# _______________________
IN HOLD
test3 asyncio
import async and ticks  OK


'''
