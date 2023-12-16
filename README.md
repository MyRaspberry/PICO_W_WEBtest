test pico w with CP900a6 webserver
https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer/issues/46#issuecomment-1857797943

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
'''
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
'''  