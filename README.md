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
