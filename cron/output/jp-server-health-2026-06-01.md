# 🇯🇵 日本服务器健康报告

**检查时间:** 2026-06-01 10:02

```
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-179-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Mon Jun  1 02:02:46 UTC 2026

  System load:  0.0                Processes:               113
  Usage of /:   42.3% of 48.27GB   Users logged in:         0
  Memory usage: 27%                IPv4 address for enp1s0: 207.56.226.147
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

5 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


=== SYSTEM ===
 02:02:48 up 2 days, 16:38,  0 users,  load average: 0.00, 0.00, 0.00
=== CPU / LOAD ===
top - 02:02:48 up 2 days, 16:38,  0 users,  load average: 0.00, 0.00, 0.00
Tasks: 112 total,   2 running, 110 sleeping,   0 stopped,   0 zombie
%Cpu(s):100.0 us,  0.0 sy,  0.0 ni,  0.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    957.3 total,     72.9 free,    211.1 used,    673.3 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    584.3 avail Mem 
0.00 0.00 0.00 2/154 38218
=== MEMORY ===
               total        used        free      shared  buff/cache   available
Mem:           957Mi       211Mi        72Mi       1.0Mi       673Mi       584Mi
Swap:             0B          0B          0B
=== DISK ===
/dev/sda1        49G   21G   28G  43% /
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
Total: 172
TCP:   9 (estab 1, closed 4, orphaned 0, timewait 3)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  1         1         0        
TCP	  5         4         1        
INET	  7         5         2        
FRAG	  0         0         0        

=== AUTH LOG (last 20 failed) ===
Jun  1 00:38:11 019e161c-739c-70d7-8f19-32f6010e538b sshd[37944]: message repeated 4 times: [ Failed password for root from 45.227.254.170 port 45384 ssh2]
Jun  1 00:43:27 019e161c-739c-70d7-8f19-32f6010e538b sshd[37954]: Failed password for root from 45.227.254.170 port 7372 ssh2
Jun  1 00:43:41 019e161c-739c-70d7-8f19-32f6010e538b sshd[37954]: message repeated 4 times: [ Failed password for root from 45.227.254.170 port 7372 ssh2]
Jun  1 00:49:07 019e161c-739c-70d7-8f19-32f6010e538b sshd[37962]: Failed password for root from 45.227.254.170 port 49410 ssh2
Jun  1 00:49:23 019e161c-739c-70d7-8f19-32f6010e538b sshd[37962]: message repeated 4 times: [ Failed password for root from 45.227.254.170 port 49410 ssh2]
Jun  1 00:52:58 019e161c-739c-70d7-8f19-32f6010e538b sshd[37975]: Failed password for root from 117.36.231.242 port 45982 ssh2
Jun  1 00:53:02 019e161c-739c-70d7-8f19-32f6010e538b sshd[37977]: Failed password for root from 117.36.231.242 port 52068 ssh2
Jun  1 00:53:06 019e161c-739c-70d7-8f19-32f6010e538b sshd[37979]: Failed password for root from 117.36.231.242 port 57432 ssh2
Jun  1 00:54:43 019e161c-739c-70d7-8f19-32f6010e538b sshd[37987]: Failed password for root from 45.148.10.152 port 21180 ssh2
Jun  1 00:54:54 019e161c-739c-70d7-8f19-32f6010e538b sshd[37987]: message repeated 4 times: [ Failed password for root from 45.148.10.152 port 21180 ssh2]
Jun  1 01:01:53 019e161c-739c-70d7-8f19-32f6010e538b sshd[37996]: Failed password for invalid user admin from 110.35.80.116 port 48878 ssh2
Jun  1 01:03:37 019e161c-739c-70d7-8f19-32f6010e538b sshd[38001]: Failed password for invalid user orangepi from 110.35.80.116 port 41574 ssh2
Jun  1 01:07:18 019e161c-739c-70d7-8f19-32f6010e538b sshd[38013]: Failed password for root from 45.148.10.152 port 61620 ssh2
Jun  1 01:07:34 019e161c-739c-70d7-8f19-32f6010e538b sshd[38013]: message repeated 4 times: [ Failed password for root from 45.148.10.152 port 61620 ssh2]
Jun  1 01:21:02 019e161c-739c-70d7-8f19-32f6010e538b sshd[38033]: Failed password for root from 35.185.64.59 port 42160 ssh2
Jun  1 01:21:02 019e161c-739c-70d7-8f19-32f6010e538b sshd[38034]: Failed password for invalid user administrator from 35.185.64.59 port 42188 ssh2
Jun  1 01:36:15 019e161c-739c-70d7-8f19-32f6010e538b sshd[38061]: Failed password for root from 45.148.10.152 port 18662 ssh2
Jun  1 01:36:29 019e161c-739c-70d7-8f19-32f6010e538b sshd[38061]: message repeated 4 times: [ Failed password for root from 45.148.10.152 port 18662 ssh2]
Jun  1 01:41:56 019e161c-739c-70d7-8f19-32f6010e538b sshd[38064]: Failed password for root from 45.227.254.170 port 40746 ssh2
Jun  1 01:42:08 019e161c-739c-70d7-8f19-32f6010e538b sshd[38064]: message repeated 4 times: [ Failed password for root from 45.227.254.170 port 40746 ssh2]
=== CRON LOG (recent) ===
Jun  1 01:17:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[38023]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
Jun  1 01:25:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[38050]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun  1 01:35:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[38057]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun  1 01:45:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[38069]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
Jun  1 01:55:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[38123]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
=== LAST REBOOT ===
         system boot  2026-05-29 09:24
```
