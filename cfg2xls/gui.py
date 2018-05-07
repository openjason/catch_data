import paramiko
import sys
import time
#import hashlib


def get_sw_conf(hostip,port,username,password):
    i = 10
    while True:
        print ("Trying to connect to %s (%i/30)" % (hostip, i))

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostip, username=username, password=password, port=port)
            print ("Connected to %s" % hostip)
            remote_conn = ssh.invoke_shell()
            output = remote_conn.recv(65535)
            print (output)
            break
        except paramiko.AuthenticationException:
            print ("Authentication failed when connecting to %s" % hostip)
            sys.exit(1)
        except:
            print ("Could not SSH to %s, waiting for it to start" % hostip)
            i += 1
            time.sleep(2)
        # If we could not connect within time limit
        if i == 30:
            print ("Could not connect to %s. Giving up" % hostip)
            sys.exit(1)

    # Send the command (non-blocking)

    more_str = bytes.fromhex('2D2D4D4F52452D2D1B5B38441B5B4B')
#    more_str = b'abc'        #2D2D4D4F52452D2D1B5B38441B5B4B
    
    fo = open("sw.log","w")
    
    remote_conn.send('show version \n')
    output = remote_conn.recv(65535)
    prompt = username + "@"
    output_str = bytes.decode(output)
    print (output_str)

    fo.write(output_str)

    remote_conn.send('cli screen length session 1600\n')
    time.sleep(0.1)
    output = remote_conn.recv(65535)
    prompt = username + "@"
    output_str = bytes.decode(output)
    print (output_str)
    fo.write(output_str)
    output_str = ''
    remote_conn.send('show curr\n')

    
    while (True):
        if prompt in output_str:
            print("hava prompt...............")
            break
        remote_conn.send(' ')
        time.sleep(0.1)
        output = remote_conn.recv(65535)
#        print(type(output))
        output = output.replace(more_str,b'')

        output_str = bytes.decode(output)

        print (output_str)
        fo.write(output_str)
#        time.sleep(1)
        

    ssh.close()

    fo.close()

if __name__ == "__main__":
    nbytes = 4096
    hostip = '192.168.151.1'
    port = 22
    username = 'cjchll' 
    password = 'Admin@007'
    command = 'show curr'

    get_sw_conf(hostip,port,username,password)
