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
