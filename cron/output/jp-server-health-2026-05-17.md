# 🇯🇵 日本服务器健康报告

**检查时间:** 2026-05-17 22:01

```
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-177-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of Sun May 17 14:01:15 UTC 2026

  System load:  0.16              Processes:               115
  Usage of /:   5.6% of 48.27GB   Users logged in:         0
  Memory usage: 24%               IPv4 address for enp1s0: 207.56.226.147
  Swap usage:   0%

 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.

   https://ubuntu.com/engage/secure-kubernetes-at-the-edge

Expanded Security Maintenance for Applications is not enabled.

8 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status

New release '24.04.4 LTS' available.
Run 'do-release-upgrade' to upgrade to it.


=== SYSTEM ===
 14:01:15 up 3 days, 23:28,  0 users,  load average: 0.23, 0.07, 0.02
=== CPU / LOAD ===
top - 14:01:16 up 3 days, 23:28,  0 users,  load average: 0.23, 0.07, 0.02
Tasks: 113 total,   1 running, 112 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0.0 us,  6.2 sy,  0.0 ni, 93.8 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
MiB Mem :    957.3 total,     96.1 free,    194.1 used,    667.2 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.    607.2 avail Mem 
0.23 0.07 0.02 1/148 42375
=== MEMORY ===
               total        used        free      shared  buff/cache   available
Mem:           957Mi       194Mi        96Mi       1.0Mi       667Mi       607Mi
Swap:             0B          0B          0B
=== DISK ===
/dev/sda1        49G  2.8G   46G   6% /
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
Total: 165
TCP:   6 (estab 2, closed 1, orphaned 0, timewait 0)

Transport Total     IP        IPv6
RAW	  1         0         1        
UDP	  1         1         0        
TCP	  5         4         1        
INET	  7         5         2        
FRAG	  0         0         0        

=== AUTH LOG (last 20 failed) ===
May 17 13:59:49 019e161c-739c-70d7-8f19-32f6010e538b sshd[42258]: Failed password for root from 43.103.43.113 port 57544 ssh2
May 17 13:59:55 019e161c-739c-70d7-8f19-32f6010e538b sshd[42260]: Failed password for root from 43.103.43.113 port 44190 ssh2
May 17 13:59:58 019e161c-739c-70d7-8f19-32f6010e538b sshd[42262]: Failed password for root from 43.103.43.113 port 44196 ssh2
May 17 14:00:02 019e161c-739c-70d7-8f19-32f6010e538b sshd[42264]: Failed password for root from 43.103.43.113 port 55478 ssh2
May 17 14:00:06 019e161c-739c-70d7-8f19-32f6010e538b sshd[42267]: Failed password for root from 43.103.43.113 port 55482 ssh2
May 17 14:00:11 019e161c-739c-70d7-8f19-32f6010e538b sshd[42269]: Failed password for root from 43.103.43.113 port 60522 ssh2
May 17 14:00:16 019e161c-739c-70d7-8f19-32f6010e538b sshd[42271]: Failed password for root from 43.103.43.113 port 60538 ssh2
May 17 14:00:20 019e161c-739c-70d7-8f19-32f6010e538b sshd[42273]: Failed password for root from 43.103.43.113 port 60548 ssh2
May 17 14:00:22 019e161c-739c-70d7-8f19-32f6010e538b sshd[42275]: Failed password for root from 43.103.43.113 port 56976 ssh2
May 17 14:00:28 019e161c-739c-70d7-8f19-32f6010e538b sshd[42277]: Failed password for root from 43.103.43.113 port 56998 ssh2
May 17 14:00:33 019e161c-739c-70d7-8f19-32f6010e538b sshd[42279]: Failed password for root from 43.103.43.113 port 47890 ssh2
May 17 14:00:38 019e161c-739c-70d7-8f19-32f6010e538b sshd[42281]: Failed password for root from 43.103.43.113 port 47896 ssh2
May 17 14:00:44 019e161c-739c-70d7-8f19-32f6010e538b sshd[42283]: Failed password for root from 43.103.43.113 port 47488 ssh2
May 17 14:00:49 019e161c-739c-70d7-8f19-32f6010e538b sshd[42285]: Failed password for root from 43.103.43.113 port 47492 ssh2
May 17 14:00:56 019e161c-739c-70d7-8f19-32f6010e538b sshd[42287]: Failed password for root from 43.103.43.113 port 32770 ssh2
May 17 14:01:02 019e161c-739c-70d7-8f19-32f6010e538b sshd[42289]: Failed password for root from 43.103.43.113 port 50398 ssh2
May 17 14:01:07 019e161c-739c-70d7-8f19-32f6010e538b sshd[42291]: Failed password for root from 43.103.43.113 port 50410 ssh2
May 17 14:01:10 019e161c-739c-70d7-8f19-32f6010e538b sshd[42293]: Failed password for root from 43.103.43.113 port 50416 ssh2
May 17 14:01:14 019e161c-739c-70d7-8f19-32f6010e538b sshd[42295]: Failed password for root from 43.103.43.113 port 46570 ssh2
May 17 14:01:17 019e161c-739c-70d7-8f19-32f6010e538b sshd[42301]: Failed password for root from 43.103.43.113 port 46572 ssh2
=== CRON LOG (recent) ===
May 17 13:17:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[41747]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
May 17 13:25:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[41754]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 17 13:35:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[41763]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 17 13:45:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[41768]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
May 17 13:55:01 019e161c-739c-70d7-8f19-32f6010e538b CRON[41976]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)
=== LAST REBOOT ===
         system boot  2026-05-13 14:32
```
