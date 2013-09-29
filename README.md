Pi Motion Detector
==================

This is a work in progress so you may have to fill in the blanks.

Requirements
------------

  * A raspberry pi
  * A raspberry pi camera + software
  * wiringpi2 python
  * A recent ffmpeg build (I built this myself, possibly only required
    for HLS which I am not using in this project yet)
  * A PIR sensor (or a button, or other 3v3 logic signal) to trigger
    capture connected to GPIO17 (wiringPi calls this pin 0)
  * I'm running this under Raspbian but I suspect you'd be better off
    doing it on Arch due to the ffmpeg requirement.

Installing
----------

I've not made the path `/capture/` configurable yet - feel free to
submit a tiny pull request.

  * `sudo mkdir -p /capture/videos/`
  * `sudo ln -s \`pwd\`/index.html /capture/index.html`
  * Serve /capture/ under nginx

Running
-------

Runs as root because of wiringpi, the `run` script handles `sudo` for
you.

`./run`

How it works
------------

The python script polls GPIO17 for a high signal. Once received it kicks
off a recording using `raspivid` piped through `psips` and then
`ffmpeg`. Whilst doing the recording it increases the light level to
maximum. When no motion has been detected for a period of time it dims
the light level to minimum again and then stops recording (via `SIGTERM`
to `raspivid` chain). It then generates a snapshot from the video to use
as a poster.

To view the videos you would serve index.html via a webserver (e.g.
nginx). A static webserver is fine for this purpose.

Lighting
--------

Lighting is controlled via PWM pin GPIO18 (wiringPi calls this pin 1).
You can hook this up to a single LED (and a resistor) but that won't
give you much light.

Instead we use the input to trigger a MOSFET that powers an LED array off
of a separate 5V source.
