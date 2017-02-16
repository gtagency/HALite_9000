import pexpect

child = pexpect.spawn('python3 KerasPlayer.py model.json weights.h5 1')
child.interact()
