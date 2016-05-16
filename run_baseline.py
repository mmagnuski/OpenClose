from __future__ import division, print_function

import os
import yaml
import random

from psychopy import visual, event, monitors, core, sound

segment_time = 60
scr_dist = 60


def send_trigger(settings, code):
	if settings['send_triggers']:
		windll.inpout32.Out32(settings['port_adress'], code)


def run(segment_time=segment_time, scr_dist=scr_dist):

    # set path to current file location
    file_path = os.path.join(*(__file__.split('\\')[:-1]))
    file_path = file_path.replace(':', ':\\')
    os.chdir(file_path)

	# check correct monitor type
	monitorList = monitors.getAllMonitors()
	if 'BENQ-XL2411' in monitorList:
	    monitor = monitors.Monitor('BENQ-XL2411', width=53., 
	        distance=scr_dist)
	    monitor.setSizePix([1920, 1080])
	else:
	    monitor = 'testMonitor'

	# create temporary window
	window = visual.Window(monitor=monitor, units="deg", fullscr=True)

	# settings
	# --------
	file_path = os.path.join(*(__file__.split('\\')[:-1]))
	file_path = file_path.replace(':', ':\\')
	file_name = os.path.join(file_path, 'settings.yaml')
	with open(file_name, 'r') as f:
		settings = yaml.load(f)
	settings['port_adress'] = int(settings['port_adress'], base=16)
	print(settings)

	# triggers
	# --------
	if settings['send_triggers']:
		try:
			from ctypes import windll
			windll.inpout32.Out32(settings['port_adress'], 111)
			core.wait(0.1)
			windll.inpout32.Out32(settings['port_adress'], 0)
		except:
			warnings.warn('Could not send test trigger. :(')
			settings['send_triggers'] = False


	# present instructions
	img = visual.ImageStim(window, image='baseline.png', size=[1169, 826],
					 units='pix', interpolate=True)
	img.draw(); window.flip()
	event.waitKeys(keyList=['left'])

	# choose seqence:
	possible_seq = ['OCCOCOOC', 'COOCOCCO']
	seq = random.sample(possible_seq, 1)[0]
	conds = {'O': 'open.wav', 'C': 'close.wav'}
	trig ={'O': 10, 'C': 11} 
	stop_sound = sound.Sound('stop.wav')

	key = event.waitKeys()

	for s in seq:
		snd = sound.Sound(conds[s])
		snd.play()

		# set trigger
		send_trigger(settings, trig[s])
		core.wait(0.1)
		send_trigger(settings, 0)

		# wait 60s
		core.wait(segment_time)
		stop_sound.play()
		wait_time = random.random() * 3 + 2.0
		core.wait(wait_time)
		resp = event.getKeys()
		if 'q' in resp:
			core.quit()

	return window

if __name__ == '__main__':
	run()
