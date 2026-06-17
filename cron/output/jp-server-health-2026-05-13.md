# 🇯🇵 日本服务器健康报告

**检查时间:** 2026-05-13 22:42

```
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-177-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Wed May 13 14:42:35 UTC 2026

  System load:  0.0               Processes:               111
  Usage of /:   5.2% of 48.27GB   Users logged in:         0
  Memory usage: 20%               IPv4 address for enp1s0: 207.56.226.147
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

New release '24.04.4 LTS' available.
Run 'do-release-upgrade' to upgrade to it.


=== SYSTEM ===
 14:42:36 up 9 min,  0 users,  load average: 0.00, 0.06, 0.07
=== CPU / LOAD ===
top - 14:42:36 up 10 min,  0 users,  load average: 0.00, 0.06, 0.07
Tasks: 109 total,   1 running, 108 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  0.0 sy,  0.0 ni,100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    957.3 total,    420.9 free,    168.1 used,    368.4 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    640.4 avail Mem 
0.00 0.06 0.07 1/141 1012
=== MEMORY ===
               total        used        free      shared  buff/cache   available
Mem:           957Mi       168Mi       420Mi       1.0Mi       368Mi       640Mi
Swap:             0B          0B          0B
=== DISK ===
/dev/sda1        49G  2.5G   46G   6% /
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
Total: 157
TCP:   6 (estab 1, closed 2, orphaned 0, timewait 1)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  1         1         0        
TCP	  4         3         1        
INET	  6         4         2        
FRAG	  0         0         0        

=== AUTH LOG (last 20 failed) ===
May 13 12:49:00 019e161c-739c-70d7-8f19-32f6010e538b sshd[59539]: message repeated 4 times: [ Failed password for root from 45.148.10.152 port 7254 ssh2]
May 13 12:50:53 019e161c-739c-70d7-8f19-32f6010e538b sshd[59545]: Failed password for root from 92.118.39.197 port 31736 ssh2
May 13 12:51:06 019e161c-739c-70d7-8f19-32f6010e538b sshd[59545]: message repeated 4 times: [ Failed password for root from 92.118.39.197 port 31736 ssh2]
May 13 12:51:39 019e161c-739c-70d7-8f19-32f6010e538b sshd[59547]: Failed password for invalid user user from 45.148.10.121 port 56380 ssh2
May 13 12:52:55 019e161c-739c-70d7-8f19-32f6010e538b sshd[59549]: Failed password for root from 2.57.122.191 port 23822 ssh2
May 13 12:53:12 019e161c-739c-70d7-8f19-32f6010e538b sshd[59549]: message repeated 4 times: [ Failed password for root from 2.57.122.191 port 23822 ssh2]
May 13 12:54:56 019e161c-739c-70d7-8f19-32f6010e538b sshd[59552]: Failed password for root from 2.57.122.192 port 64452 ssh2
May 13 12:54:58 019e161c-739c-70d7-8f19-32f6010e538b sshd[59552]: Failed password for root from 2.57.122.192 port 64452 ssh2
May 13 12:55:03 019e161c-739c-70d7-8f19-32f6010e538b sshd[59552]: Failed password for root from 2.57.122.192 port 64452 ssh2
May 13 12:55:10 019e161c-739c-70d7-8f19-32f6010e538b sshd[59552]: message repeated 2 times: [ Failed password for root from 2.57.122.192 port 64452 ssh2]
May 13 12:56:57 019e161c-739c-70d7-8f19-32f6010e538b sshd[59559]: Failed password for root from 2.57.122.195 port 23986 ssh2
May 13 12:57:11 019e161c-739c-70d7-8f19-32f6010e538b sshd[59559]: message repeated 4 times: [ Failed password for root from 2.57.122.195 port 23986 ssh2]
May 13 12:58:59 019e161c-739c-70d7-8f19-32f6010e538b sshd[59562]: Failed password for root from 2.57.122.190 port 26498 ssh2
May 13 12:59:13 019e161c-739c-70d7-8f19-32f6010e538b sshd[59562]: message repeated 4 times: [ Failed password for root from 2.57.122.190 port 26498 ssh2]
May 13 13:01:00 019e161c-739c-70d7-8f19-32f6010e538b sshd[59565]: Failed password for root from 45.148.10.157 port 23376 ssh2
May 13 13:01:03 019e161c-739c-70d7-8f19-32f6010e538b sshd[59565]: Failed password for root from 45.148.10.157 port 23376 ssh2
May 13 13:09:24 019e161c-739c-70d7-8f19-32f6010e538b sshd[59620]: Failed password for invalid user pi from 61.83.195.160 port 47816 ssh2
May 13 13:09:24 019e161c-739c-70d7-8f19-32f6010e538b sshd[59622]: Failed password for invalid user pi from 61.83.195.160 port 47834 ssh2
May 13 13:25:15 019e161c-739c-70d7-8f19-32f6010e538b sshd[59636]: Failed password for root from 45.148.10.121 port 55020 ssh2
May 13 13:58:13 019e161c-739c-70d7-8f19-32f6010e538b sshd[59660]: Failed password for invalid user ubnt from 45.148.10.121 port 35000 ssh2
=== CRON LOG (recent) ===
May 13 14:31:10 019e161c-739c-70d7-8f19-32f6010e538b cron[66671]: (CRON) INFO (pidfile fd = 3)
May 13 14:31:10 019e161c-739c-70d7-8f19-32f6010e538b cron[66671]: (CRON) INFO (Skipping @reboot jobs -- not system startup)
May 13 14:33:01 019e161c-739c-70d7-8f19-32f6010e538b cron[616]: (CRON) INFO (pidfile fd = 3)
May 13 14:33:01 019e161c-739c-70d7-8f19-32f6010e538b cron[616]: (CRON) INFO (Running @reboot jobs)
May 13 14:35:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[875]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
=== LAST REBOOT ===
         system boot  2026-05-13 14:32
```
