
docker pull sheldonhh/smu_dag_sbip
docker run -it -d --name smudag sheldonhh/smu_dag_sbip

# sync btc raw data
docker exec smudag bash /root/start_rawbtc.sh

# preprocess of raw data
docker exec smudag  /etc/init.d/cron start


# view log of raw data
docker exec smudag tail /root/rawbtc.log
# view log of blocksci preprocess
docker exec smudag tail /root/hourly_blocksci.log

