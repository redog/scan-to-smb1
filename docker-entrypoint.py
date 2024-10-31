#!/usr/bin/env python3

import os, subprocess

linuxUserId = os.getenv('USERID')
linuxGroupId = os.getenv('GROUPID')
sambaUsername = os.getenv('SAMBA_USERNAME')
sambaPassword = os.getenv('SAMBA_PASSWORD')

totalProxyCount = 0
enabledProxyCount = 0

i = 0
while True:
  i = i + 1
  shareEnable = os.getenv('PROXY{}_ENABLE'.format(i))
  if shareEnable == None:
    break
  totalProxyCount += 1

  if not shareEnable == "1":
    continue
  enabledProxyCount += 1

  shareName = os.getenv('PROXY{}_SHARE_NAME'.format(i))
  shareDirectory = '/share{}'.format(i)
  remotePath = os.getenv('PROXY{}_REMOTE_PATH'.format(i))
  remoteDomain = os.getenv('PROXY{}_REMOTE_DOMAIN'.format(i))
  remoteUsername = os.getenv('PROXY{}_REMOTE_USERNAME'.format(i))
  remotePassword = os.getenv('PROXY{}_REMOTE_PASSWORD'.format(i))
  remoteMount = '/remote{}'.format(i)

  # SMB Mount
  print("Mounting '{share}' with user '{domain}\\{username}' at '{directory}'".format(
    share = remotePath,
    domain = remoteDomain,
    username = remoteUsername,
    directory = remoteMount
  ))

  # Ensure the mount point exists and has the correct permissions
    # This never worked. Created volume instead
    #try:
    #os.makedirs(remoteMount, exist_ok=True)  # Create directory recursively if needed
    #    #cmd = ["chown", f"{linuxUserId}:{linuxGroupId}", remoteMount]  
    #    #subprocess.check_call(cmd)
    #cmd = ["ls", "-l", "/remote1"]
    #subprocess.check_call(cmd)
    #
    #except (subprocess.CalledProcessError, OSError) as e:  # Catch potential OSError from makedirs
    #  print(f"Error creating or changing ownership of '{remoteMount}': {e}")
    #  exit(1)

    #if not os.path.exists(remoteMount):
    #os.mkdir(remoteMount)
    #subprocess.call("chown {}:{} {}".format(linuxUserId, linuxGroupId, remoteMount), shell=True)

  try:
    # Construct the mount command with more careful escaping
    cmd = [
        "mount.cifs", "-o", "username='{username}',password='{password}',domain='{domain}'".format(
            username=remoteUsername,
            password=remotePassword,
            domain=remoteDomain
            ),
         "'{share}'".format(share=remotePath),  # Escape the share path
         "'{directory}'".format(directory=remoteMount)  # Escape the directory path
        ]
    ret = subprocess.run(
            cmd,
            capture_output=True,  # Capture stdout and stderr
            text=True             # Decode output as text
        )

    if ret.returncode != 0:
            print("Mounting failed!")
            print("Error output:", ret.stderr)  # Print the error output from the command
            os.rmdir(remoteMount)
            exit(1)
    else:
            print("Mounting successful!")

  except Exception as e:
        print("An unexpected error occurred:", e)
        os.rmdir(remoteMount)
        exit(1)

  # Samba Share
  print("Setting up share '{share}' for User '{username}' at '{directory}'".format(
    share = shareName,
    username = sambaUsername,
    directory = shareDirectory
  ))
  if not os.path.exists(shareDirectory):
    os.mkdir(shareDirectory)
  subprocess.call("chown {}:{} {}".format(linuxUserId, linuxGroupId, shareDirectory), shell=True)
  os.environ['SHARE{}'.format(i)] = "{};{};yes;no;no;{}".format(shareName, shareDirectory, sambaUsername)

print("{}/{} enabled Proxies.".format(enabledProxyCount, totalProxyCount))
if enabledProxyCount == 0:
  exit(0)

# Global Samba settings
os.environ['USER'] = "{};{}".format(sambaUsername, sambaPassword)
os.environ['RECYCLE'] = "x" # disable recycle bin
os.environ['SMB'] = "x" # disable SMB2 minimum version

subprocess.call('/usr/bin/supervisord -c /etc/supervisord.conf', shell=True)
