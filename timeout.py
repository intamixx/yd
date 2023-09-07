#!/usr/bin/env python3
import subprocess, threading, sys, os, signal, atexit

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            print ('Thread started')
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            self.out = self.process.stdout.read()
            self.out = (self.out.decode('UTF-8'))
            self.process.communicate()
            print ('Thread finished')

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print ('Terminating process')
            self.process.terminate()
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            os.kill(os.getpid(self.process.pid), signal.SIGTERM)
            thread.join()
        #print (self.process.returncode)
        return (self.process.returncode, self.out)

#command = Command("ls -al;uname -a;hostname;sleep 3")
#command = Command("echo 'Process started'; sleep 10; echo 'Process finished'")

container = "mpioperator/mpi-pi"
container_args = "/home/mpiuser/pi"

cmd_str = "docker pull {}".format(container)
print ("Launching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=5)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))
#print (output[0])
#print (output[1])

cmd_str = "docker run --rm -v /mnt:/mnt {} {}".format(container, container_args)
print ("Launching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=5)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))

cmd_str = "ls -la"
print ("Launching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=5)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))
sys.exit(0)
