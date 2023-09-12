#! /usr/bin/env python3
import subprocess, threading, sys, os, signal, atexit, shutil
import boto3
from boto3 import client
from io import BytesIO

aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
container = os.environ['CONTAINER']

files_to_download = os.environ['FILES_TO_DOWNLOAD']
files_to_upload = os.environ['FILES_TO_UPLOAD']

container_args = sys.argv[2]

if not container_args:
    print ("No arguments. No script or executable supplied for a container run.")
    sys.exit(1)

def error():
    print ("OH NO, timeout?")
    sys.exit(1)

def upload(local_file_name, s3_bucket, s3_object_key):

    my_abs_path = ("{}/{}".format(os.getcwd(),local_file_name))
    try:
        os.path.isfile(my_abs_path)
    except:
        print("{} does not exist locally or not readable".format(my_abs_path))
        sys.exit(1)

    total_length = os.path.getsize(local_file_name)
    uploaded = 0

    def progress(chunk):
        nonlocal uploaded
        uploaded += chunk
        done = int(50 * uploaded / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
        sys.stdout.flush()

    print(f'Uploading {s3_object_key}')
    #s3_client.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)
    s3_client.upload_file(local_file_name, s3_bucket, s3_object_key, Callback=progress)

def download(local_file_name, s3_bucket, s3_object_key):

    try:
        meta_data = s3_client.head_object(Bucket=s3_bucket, Key=s3_object_key)
    except:
        print("{} does not exist in bucket or not readable".format(s3_object_key))
        sys.exit(1)
    total_length = int(meta_data.get('ContentLength', 0))
    downloaded = 0

    def progress(chunk):
        nonlocal downloaded
        downloaded += chunk
        done = int(50 * downloaded / total_length)
        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
        sys.stdout.flush()

    print(f'Downloading {s3_object_key}')
    with open(local_file_name, 'wb') as f:
        s3_client.download_fileobj(s3_bucket, s3_object_key, f, Callback=progress)

class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout, shell):
        def target():
            print ('Thread started')
            self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)
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
            error()
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            os.kill(os.getpid(self.process.pid), signal.SIGTERM)
            thread.join()
        #print (self.process.returncode)
        return (self.process.returncode, self.out)

#command = Command("ls -al;uname -a;hostname;sleep 3")
#command = Command("echo 'Process started'; sleep 10; echo 'Process finished'")

import boto3

s3 = boto3.client('s3')
s3_client = boto3.client('s3',
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key )


cmd_str = ("docker pull {}".format(container))
cmd_str = cmd_str.split()
print ("\nLaunching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=50, shell=False)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))
#print (output[0])
#print (output[1])

#local_file_name = 'application.yaml'
s3_bucket = 's3-kingston-yd-test01'
#s3_object_key = 'application.yaml'

s3_file_list = files_to_download.split(",")
for s3_file_name in s3_file_list:
    #download(s3_file_name, s3_bucket, s3_object_key)
    download(s3_file_name, s3_bucket, s3_file_name)
    shutil.copy(s3_file_name, "/var/opt/yellowdog/agent/mnt")

# Copy file for into volume mount directory for container
#shutil.copy(local_file_name, "/var/opt/yellowdog/agent/mnt")

#cmd_str = ("docker run --rm -v /var/opt/yellowdog/agent/mnt:/mnt {} {} | tee -a /var/opt/yellowdog/agent/output1.txt".format(container, container_args))
cmd_str = ("docker run --rm -v /var/opt/yellowdog/agent/mnt:/mnt {} {}".format(container, container_args))
cmd_str = cmd_str.split()
print ("\nLaunching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=1, shell=False)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))

print ("\nUploading results back to S3 bucket")
#local_file_name = '/mnt/output1.txt'
#s3_bucket = 's3-kingston-yd-test01'
#s3_object_key = 'output1.txt'

local_file_list = files_to_upload.split(",")
for local_file_name in local_file_list:
    upload(local_file_name, s3_bucket, local_file_name)

sys.exit(0)



cmd_str = "ls -la"
print ("Launching: {}".format(cmd_str))
command = Command(cmd_str)
threads = []
output = command.run(timeout=50)
print ("Return code: {}".format(output[0]))
print ("Output:\n {}".format(output[1]))
sys.exit(0)
