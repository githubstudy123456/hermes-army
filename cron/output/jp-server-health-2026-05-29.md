# 🇯🇵 日本服务器健康报告

**检查时间:** 2026-05-29 10:02

```
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-177-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Fri May 29 02:01:57 UTC 2026

  System load:  0.0               Processes:               112
  Usage of /:   6.3% of 48.27GB   Users logged in:         0
  Memory usage: 25%               IPv4 address for enp1s0: 207.56.226.147
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

1 update can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


*** System restart required ***
=== SYSTEM ===
 02:02:00 up 15 days, 11:29,  0 users,  load average: 0.00, 0.00, 0.00
=== CPU / LOAD ===
top - 02:02:00 up 15 days, 11:29,  0 users,  load average: 0.24, 0.05, 0.02
Tasks: 111 total,   2 running, 109 sleeping,   0 stopped,   0 zombie
%Cpu(s):100.0 us,  0.0 sy,  0.0 ni,  0.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    957.3 total,    142.4 free,    191.3 used,    623.6 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    603.2 avail Mem 
0.24 0.05 0.02 2/147 157351
=== MEMORY ===
               total        used        free      shared  buff/cache   available
Mem:           957Mi       192Mi       140Mi       1.0Mi       624Mi       601Mi
Swap:             0B          0B          0B
=== DISK ===
/dev/sda1        49G  3.1G   46G   7% /
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
LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=677,fd=3))            
LISTEN 0      4096               *:443             *:*    users:(("xray",pid=636,fd=4))            
LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=677,fd=4))            
=== NETWORK ===
Total: 171
TCP:   12 (estab 3, closed 4, orphaned 0, timewait 0)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  1         1         0        
TCP	  8         4         4        
INET	  10        5         5        
FRAG	  0         0         0        

=== AUTH LOG (last 20 failed) ===
May 29 01:44:29 019e161c-739c-70d7-8f19-32f6010e538b sshd[157213]: Failed password for invalid user user from 50.116.106.59 port 52518 ssh2
May 29 01:44:41 019e161c-739c-70d7-8f19-32f6010e538b sshd[157215]: Failed password for root from 45.227.254.170 port 63916 ssh2
May 29 01:44:55 019e161c-739c-70d7-8f19-32f6010e538b sshd[157215]: message repeated 4 times: [ Failed password for root from 45.227.254.170 port 63916 ssh2]
May 29 01:45:05 019e161c-739c-70d7-8f19-32f6010e538b sshd[157220]: Failed password for invalid user len from 195.178.191.5 port 34142 ssh2
May 29 01:45:57 019e161c-739c-70d7-8f19-32f6010e538b sshd[157222]: Failed password for invalid user ibrahim from 50.116.106.59 port 53606 ssh2
May 29 01:46:25 019e161c-739c-70d7-8f19-32f6010e538b sshd[157224]: Failed password for invalid user UBUNTU from 195.178.191.5 port 52482 ssh2
May 29 01:47:01 019e161c-739c-70d7-8f19-32f6010e538b sshd[157226]: Failed password for invalid user user from 2.57.121.25 port 52206 ssh2
May 29 01:47:05 019e161c-739c-70d7-8f19-32f6010e538b sshd[157226]: Failed password for invalid user user from 2.57.121.25 port 52206 ssh2
May 29 01:47:08 019e161c-739c-70d7-8f19-32f6010e538b sshd[157226]: Failed password for invalid user user from 2.57.121.25 port 52206 ssh2
May 29 01:47:10 019e161c-739c-70d7-8f19-32f6010e538b sshd[157226]: Failed password for invalid user user from 2.57.121.25 port 52206 ssh2
May 29 01:47:15 019e161c-739c-70d7-8f19-32f6010e538b sshd[157226]: Failed password for invalid user user from 2.57.121.25 port 52206 ssh2
May 29 01:47:25 019e161c-739c-70d7-8f19-32f6010e538b sshd[157228]: Failed password for invalid user user2 from 50.116.106.59 port 54704 ssh2
May 29 01:47:41 019e161c-739c-70d7-8f19-32f6010e538b sshd[157230]: Failed password for root from 195.178.191.5 port 34840 ssh2
May 29 01:48:48 019e161c-739c-70d7-8f19-32f6010e538b sshd[157232]: Failed password for invalid user admin from 50.116.106.59 port 55794 ssh2
May 29 01:50:11 019e161c-739c-70d7-8f19-32f6010e538b sshd[157235]: Failed password for invalid user len from 50.116.106.59 port 56882 ssh2
May 29 01:50:25 019e161c-739c-70d7-8f19-32f6010e538b sshd[157237]: Failed password for root from 92.118.39.236 port 42894 ssh2
May 29 01:50:39 019e161c-739c-70d7-8f19-32f6010e538b sshd[157237]: message repeated 4 times: [ Failed password for root from 92.118.39.236 port 42894 ssh2]
May 29 01:56:13 019e161c-739c-70d7-8f19-32f6010e538b sshd[157246]: Failed password for root from 45.148.10.141 port 26404 ssh2
May 29 01:56:27 019e161c-739c-70d7-8f19-32f6010e538b sshd[157246]: message repeated 4 times: [ Failed password for root from 45.148.10.141 port 26404 ssh2]
May 29 02:01:59 019e161c-739c-70d7-8f19-32f6010e538b sshd[157249]: Failed password for root from 45.148.10.147 port 12098 ssh2
=== CRON LOG (recent) ===
May 29 01:17:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[157034]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
May 29 01:25:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[157079]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 29 01:35:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[157145]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 29 01:45:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[157218]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 29 01:55:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[157243]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
=== LAST REBOOT ===
         system boot  2026-05-13 14:32
```
