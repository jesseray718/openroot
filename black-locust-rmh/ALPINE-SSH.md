# Black Locust RMH — Alpine SSH Bridge
Target: Alpine container via Termux/Shizuku
Port: 8022
Command sequence:
sshd -p 8022
# then from Kai9000: Settings → SSH → host alias black-locust
# push: rsync -avz -e "ssh -p 8022" . user@localhost:\~/black-locust-rmh/
