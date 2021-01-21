#!/bin/bash

# ASCII escape characters
ascii_red=31
ascii_green=32
ascii_yellow=33
ascii_esc="\u1B["

# Colourful logging
function print(){
	if [[ $1 == "Error: "* ]]; then
		color=$ascii_red
	elif [[ $1 == "Warning: "* ]]; then
		color=$ascii_yellow
	else
		color=$ascii_green
	fi
	printf "${ascii_esc}${color}m${1}${ascii_esc}0m\r\n"
}

print "Starting captcha generation of training set..."
printf "GET /captcha/?is_training=1&captcha_num=2500 HTTP/1.0\r\n\r\n" | nc localhost 80

print "Starting captcha generation of test set..."
printf "GET /captcha/?is_training=0&captcha_num=250 HTTP/1.0\r\n\r\n" | nc localhost 80

print "Captcha generation finished successfully."

python3 preprocessor.py
print "Preprocessing task (noise removing and letter extracting) finished successfully."
