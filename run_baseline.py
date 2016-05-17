from __future__ import division, print_function

import os
import yaml
import random
import warnings

from psychopy import visual, event, monitors, core, sound

segment_time = 60
scr_dist = 60


# settings
# --------
file_path = os.path.join(*(__file__.split('\\')[:-1]))
file_path = file_path.replace(':', ':\\')
file_name = os.path.join(file_path, 'settings.yaml')
with open(file_name, 'r') as f:
    settings = yaml.load(f)
settings['port_adress'] = int(settings['port_adress'], base=16)

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


def send_trigger(settings, code):
    if settings['send_triggers']:
        windll.inpout32.Out32(settings['port_adress'], code)


def get_subject_id():
    from psychopy import gui
    myDlg = gui.Dlg(title="Subject Info", size = (800,600))
    myDlg.addText('Informacje o osobie badanej')
    myDlg.addField('ID:')
    myDlg.show()  # show dialog and wait for OK or Cancel

    if myDlg.OK:  # Ok was pressed
        return myDlg.data[0]
    else:
        core.quit()


def run(segment_time=segment_time, scr_dist=scr_dist, debug=False):

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
    window.mouseVisible = False

    # present instructions
    img = visual.ImageStim(window, image=os.path.join('instr', 'baseline.png'),
                           size=[1169, 826], units='pix', interpolate=True)
    img.draw(); window.flip()
    event.waitKeys(keyList=['right'])
    window.flip()

    # choose seqence:
    possible_seq = ['OCCOCOOC', 'COOCOCCO']
    seq = random.sample(possible_seq, 1)[0]
    sounds = [os.path.join('snd', s) for s in ['open.wav', 'close.wav']]
    conds = {'O': sounds[0], 'C': sounds[1]}
    trig ={'O': 10, 'C': 11}
    stop_sound = sound.Sound(os.path.join('snd', 'stop.wav'))

    for s in seq:
        # check for quit
        resp = event.getKeys()
        if debug and 'q' in resp:
            core.quit()

        # play open/close sound
        snd = sound.Sound(conds[s])
        snd.play()

        # set trigger
        send_trigger(settings, trig[s])
        core.wait(0.1)
        send_trigger(settings, 0)

        # wait segment_time, play ring and then wait break time
        core.wait(segment_time)
        stop_sound.play()
        if not debug:
            wait_time = random.random() * 3 + 3.5
        else:
            wait_time = 0.5
        core.wait(wait_time)

    return window

if __name__ == '__main__':
    run()
