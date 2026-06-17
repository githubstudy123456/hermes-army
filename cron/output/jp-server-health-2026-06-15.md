# 🇯🇵 日本服务器健康报告

**检查时间:** 2026-06-15 10:02

```
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-179-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Mon Jun 15 02:02:24 UTC 2026

  System load:  0.01               Processes:               113
  Usage of /:   16.3% of 48.27GB   Users logged in:         0
  Memory usage: 28%                IPv4 address for enp1s0: 207.56.226.147
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

16 updates can be applied immediately.
3 of these updates are standard security updates.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

New release '24.04.4 LTS' available.
Run 'do-release-upgrade' to upgrade to it.


*** System restart required ***
=== SYSTEM ===
 02:02:25 up 16 days, 16:38,  0 users,  load average: 0.01, 0.01, 0.00
=== CPU / LOAD ===
top - 02:02:25 up 16 days, 16:38,  0 users,  load average: 0.01, 0.01, 0.00
Tasks: 111 total,   1 running, 110 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    957.3 total,     76.0 free,    214.1 used,    667.2 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    579.6 avail Mem 
0.01 0.01 0.00 1/154 147639
=== MEMORY ===
               total        used        free      shared  buff/cache   available
Mem:           957Mi       214Mi        76Mi       1.0Mi       667Mi       579Mi
Swap:             0B          0B          0B
=== DISK ===
/dev/sda1        49G  7.9G   41G  17% /
/dev/sda15      105M  6.1M   99M   6% /boot/efi
=== SERVICES ===
active
Xray: ACTIVE
active
SSH: ACTIVE
inactive
Docker: INACTIVE
  UNIT LOAD ACTIVE SUB DESCRIPTION
0 loaded units listed.
=== XRAY STATUS ===
LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=684,fd=3))              
LISTEN 0      4096               *:443             *:*    users:(("xray",pid=637,fd=4))              
LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=684,fd=4))              
=== NETWORK ===
Total: 174
TCP:   14 (estab 6, closed 4, orphaned 0, timewait 3)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  1         1         0        
TCP	  10        9         1        
INET	  12        10        2        
FRAG	  0         0         0        

=== AUTH LOG (last 20 failed) ===
Jun 15 01:46:48 019e161c-739c-70d7-8f19-32f6010e538b sshd[147500]: Failed password for invalid user itadmin from 103.167.89.222 port 40294 ssh2
Jun 15 01:48:14 019e161c-739c-70d7-8f19-32f6010e538b sshd[147502]: Failed password for root from 119.205.179.217 port 47188 ssh2
Jun 15 01:49:08 019e161c-739c-70d7-8f19-32f6010e538b sshd[147505]: Failed password for invalid user ajay from 103.167.89.222 port 40446 ssh2
Jun 15 01:50:28 019e161c-739c-70d7-8f19-32f6010e538b sshd[147508]: Failed password for root from 45.148.10.147 port 37986 ssh2
Jun 15 01:50:39 019e161c-739c-70d7-8f19-32f6010e538b sshd[147508]: message repeated 4 times: [ Failed password for root from 45.148.10.147 port 37986 ssh2]
Jun 15 01:50:43 019e161c-739c-70d7-8f19-32f6010e538b sshd[147510]: Failed password for invalid user peace from 119.205.179.217 port 46988 ssh2
Jun 15 01:51:25 019e161c-739c-70d7-8f19-32f6010e538b sshd[147512]: Failed password for invalid user sol from 80.94.92.184 port 52702 ssh2
Jun 15 01:51:28 019e161c-739c-70d7-8f19-32f6010e538b sshd[147514]: Failed password for root from 103.167.89.222 port 40610 ssh2
Jun 15 01:53:10 019e161c-739c-70d7-8f19-32f6010e538b sshd[147519]: Failed password for invalid user user2 from 119.205.179.217 port 48788 ssh2
Jun 15 01:53:49 019e161c-739c-70d7-8f19-32f6010e538b sshd[147521]: Failed password for root from 103.167.89.222 port 40764 ssh2
Jun 15 01:55:37 019e161c-739c-70d7-8f19-32f6010e538b sshd[147529]: Failed password for root from 119.205.179.217 port 50050 ssh2
Jun 15 01:56:08 019e161c-739c-70d7-8f19-32f6010e538b sshd[147531]: Failed password for invalid user solana from 80.94.92.184 port 55112 ssh2
Jun 15 01:56:12 019e161c-739c-70d7-8f19-32f6010e538b sshd[147533]: Failed password for root from 103.167.89.222 port 40924 ssh2
Jun 15 01:57:17 019e161c-739c-70d7-8f19-32f6010e538b sshd[147535]: Failed password for root from 45.148.10.147 port 30684 ssh2
Jun 15 01:57:26 019e161c-739c-70d7-8f19-32f6010e538b sshd[147535]: message repeated 4 times: [ Failed password for root from 45.148.10.147 port 30684 ssh2]
Jun 15 01:58:00 019e161c-739c-70d7-8f19-32f6010e538b sshd[147537]: Failed password for root from 119.205.179.217 port 51640 ssh2
Jun 15 01:58:30 019e161c-739c-70d7-8f19-32f6010e538b sshd[147539]: Failed password for root from 103.167.89.222 port 41084 ssh2
Jun 15 02:00:28 019e161c-739c-70d7-8f19-32f6010e538b sshd[147545]: Failed password for root from 119.205.179.217 port 42748 ssh2
Jun 15 02:00:30 019e161c-739c-70d7-8f19-32f6010e538b sshd[147543]: Failed password for invalid user solana from 80.94.92.184 port 57530 ssh2
Jun 15 02:00:53 019e161c-739c-70d7-8f19-32f6010e538b sshd[147548]: Failed password for root from 103.167.89.222 port 41240 ssh2
=== CRON LOG (recent) ===
Jun 15 01:17:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[147340]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
Jun 15 01:25:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[147376]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun 15 01:35:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[147453]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun 15 01:45:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[147494]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun 15 01:55:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[147526]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
=== LAST REBOOT ===
         system boot  2026-05-29 09:24
```
