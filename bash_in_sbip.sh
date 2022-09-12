# 0. pull docker image with tag 0912
docker pull sheldonhh/smu_dag_sbip:0912

# 1. start ssh-server with port open on host
docker run -it -d --name smudag -p [PORT_FOR_REMOTE_ACCESS]:22 sheldonhh/smu_dag_sbip:0912 

# 2. sync btc raw data
docker exec smudag bash /root/start_rawbtc.sh

# 3. preprocess of raw data
docker exec smudag  /etc/init.d/cron start



# view log of raw data
docker exec smudag tail /root/rawbtc.log
# view log of blocksci preprocess
docker exec smudag tail /root/hourly_blocksci.log

