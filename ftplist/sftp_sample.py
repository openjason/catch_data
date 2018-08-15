

paramiko.SFTPClient

Example:

import paramiko
paramiko.util.log_to_file('/tmp/paramiko.log')

# Open a transport

host = "example.com"
port = 22
transport = paramiko.Transport((host, port))

# Auth

password = "foo"
username = "bar"
transport.connect(username = username, password = password)

# Go!

sftp = paramiko.SFTPClient.from_transport(transport)

# Download

filepath = '/etc/passwd'
localpath = '/home/remotepasswd'
sftp.get(filepath, localpath)

# Upload

filepath = '/home/foo.jpg'
localpath = '/home/pony.jpg'
sftp.put(localpath, filepath)

# Close

sftp.close()
transport.close()

