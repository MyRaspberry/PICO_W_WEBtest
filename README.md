test pico w with CP900a6 webserver

[issues](https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/issues/46#issuecomment-1857797943)

system files:
```
flash_nuke.uf2

adafruit-circuitpython-raspberry_pi_pico_w-en_US-9.0.0-alpha.6.uf2

adafruit-circuitpython-bundle-9.x-mpy-20231215.zip
```

boot_out.txt
```
Adafruit CircuitPython 9.0.0-alpha.6 on 2023-12-12; Raspberry Pi Pico W with rp2040

Board ID:raspberry_pi_pico_w

```


testresults:

-a-<br>
1Mloop only<br>
9.8 sec mem: 47952 mem low: 45072<br>
-b-<br>
1Mloop and loop1<br>
18.0 sec mem:47800 mem low: 45206<br>
-c-<br>
1Mloop and loop1 run_webserver<br>
18.7 sec mem: 47600 mem low: 47584<br>
-d-<br>
1Mloop and loop1 run_webserver and webpage / autorefresh 5 sec<br>
21.4 sec mem: 52320 mem low: 47584<br>

no gc.collect at run_webserver mem: 52240 mem low:46672<br>
-e-<br>
need change loopt1 from 1000 to 10 to have a 1 sec tick<br>
run_webserver in main loop ( delete 2 front [tab] )<br>
1Mloop and loop1<br>
226.1 sec mem: 52480 mem low: 18912<br>
-e+f-<br>
start webpage / autorefresh 5 sec but sometimes need 20 sec?<br>
233.4 sec mem: 52480 mem low: 27872<br>
-e+f+g-<br>
test mem for it without gc.collect<br>
mem: 52160 mem low: 672 ? // mem runs down but autorecovers ?<br>

!!! server.poll() is a timing and memory pig !!!<br>

[memory downloop](http://kll.byethost7.com/kllfusion01/downloads/server_poll_memory.png)

test 2

replace /adafruit_httpserver/server.mpy with server.py<br>
from https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/blame/main/adafruit_httpserver/server.py<br>
? how i know that is the one used in adafruit-circuitpython-bundle-9.x-mpy-20231215.zip<br>

change:<br>
    def __init__(<br>
        self, socket_source: Protocol, root_path: str = None, *, debug: bool = True # KLL test False<br>
    ) -> None:<br>
see:<br>
www served dynamic index.html<br>
192.168.1.8 -- "GET /" 373 -- "200 OK" 1174 -- 293ms<br>
BUT<br>
```
            if self.debug:
                _debug_response_sent(response, _debug_end_time - _debug_start_time)
```
i not see timing for every poll(), only for page request, how to do?<br>
