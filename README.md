# DAG_SMU

## Setup Server done before deploying to SBIP
https://hub.docker.com/r/sheldonhh/smu_dag_sbip
docker pull sheldonhh/smu_dag_sbip



## Initalize Docker and r
```bash
docker pull sheldonhh/smu_dag_sbip
docker run -it -d --name smudag sheldonhh/smu_dag_sbip

# sync btc raw data
docker exec smudag bash /root/start_rawbtc.sh

# preprocess of raw data
docker exec smudag  /etc/init.d/cron start
```

## tail logs
```bash
# view log of raw data of step 1
docker exec smudag tail /root/0920_rawbtc.log
# view log of blocksci preprocess of step 2
docker exec smudag tail /root/hourly_blocksci.log
```

## storage system structure SBIP Ubuntu(docker) server 
two 
```bash
/dev/md1p1      3.6T  680G  2.8T  20% /data1
/dev/md2p1      3.6T   89M  3.4T   1% /data2
```

## file structure under /root directory
/root
│   start_rawbtc.sh # step 1 raw btc data synchronization
│   0920_rawbtc.log # log from step 1
│    
│   start_step_34.sh # step 3, 4
│   0921_step34.log # log from step 3, 4
│ w
└───data_bitcoin 
BlockSci
/data1
|   
└───data_bitcoin  # directory for raw btc synchronization
│
└───folder1
│   │   file011.txt
│   │   file012.txt
│   │
│   └───subfolder1
│       │   file111.txt
│       │   file112.txt
│       │   ...
│   
└───folder2
    │   file021.txt
    │   file022.txt


## step 2 json file in /root/bloksci.config 
```json
{
    "chainConfig": {
        "coinName": "bitcoin",
        "dataDirectory": "/root/blocksci_output",
        "pubkeyPrefix": [
            0
        ],
        "scriptPrefix": [
            5
        ],
        "segwitActivationHeight": 481824,
        "segwitPrefix": "bc"
    },
    "parser": {
        "disk": {
            "blockMagic": 3652501241,
            "coinDirectory": "/data1/data_bitcoin",
            "hashFuncName": "doubleSha256"
        },
        "maxBlockNum": 0
    },
    "version": 5
}
```
## Command in `crontab`
```bash
# m h  dom mon dow   command
0 * * * * /usr/bin/blocksci_parser "/root/bloksci.config" update >> /root/hourly_blocksci.log
```