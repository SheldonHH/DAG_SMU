# DAG_SMU
- [DAG_SMU](#dag_smu)
  - [Setup Server done before deploying to SBIP](#setup-server-done-before-deploying-to-sbip)
  - [For SBIP-side](#for-sbip-side)
    - [pull and start docker container (For SBIP Dumitrel Loghin only)](#pull-and-start-docker-container-for-sbip-dumitrel-loghin-only)
    - [Execute outside Docker (For SBIP Dumitrel Loghin only)](#execute-outside-docker-for-sbip-dumitrel-loghin-only)
    - [tail logs (For SBIP Dumitrel Loghin only)](#tail-logs-for-sbip-dumitrel-loghin-only)
  - [for SMU DAG Team](#for-smu-dag-team)
    - [Login](#login)
    - [Execution](#execution)
      - [Step 1. raw btc synchronization](#step-1-raw-btc-synchronization)
      - [Step 2. blocksci hourly preprocessing](#step-2-blocksci-hourly-preprocessing)
      - [Step 3. network_data_part_every_block.py](#step-3-network_data_part_every_blockpy)
  - [Ubuntu (Docker) Specification and Structure](#ubuntu-docker-specification-and-structure)
    - [storage system structure SBIP Ubuntu(docker) server](#storage-system-structure-sbip-ubuntudocker-server)
    - [file structure under /root directory](#file-structure-under-root-directory)
    - [config for blocksci preprocess in `/root/bloksci.config`](#config-for-blocksci-preprocess-in-rootbloksciconfig)
  - [Command in `crontab`](#command-in-crontab)
## Setup Server done before deploying to SBIP
pre-created docker image: https://hub.docker.com/r/sheldonhh/smu_dag_sbip    
or Ubuntu official image (⚠️ be aware of Ubuntu version ⚠️): 
https://hub.docker.com/_/ubuntu


## For SBIP-side

### pull and start docker container (For SBIP Dumitrel Loghin only)
```bash
docker pull sheldonhh/smu_dag_sbip
docker run -it -d --name smudag sheldonhh/smu_dag_sbip
## start sshd
service ssh start
service ssh restart
/usr/sbin/sshd -D
```
### Execute outside Docker (For SBIP Dumitrel Loghin only)
```
# Step 1 sync btc raw data
docker exec smudag bash /root/start_rawbtc.sh

# Step 2: preprocess of raw data
docker exec smudag  /etc/init.d/cron start

# Step 3: preprocess of raw data
docker exec smudag  /etc/init.d/cron start
```


### tail logs (For SBIP Dumitrel Loghin only)
```bash
# view log of raw data of step 1
docker exec smudag tail /root/0920_rawbtc.log
# view log of blocksci preprocess of step 2
docker exec smudag tail /root/hourly_blocksci.log
```

## for SMU DAG Team 

### Login
```bash
ssh -p 80 root@xxx.xxx.xxx.xxx
```

### Execution
#### Step 1. raw btc synchronization
```bash
start_rawbtc.sh
## view log
tail -f 0920_rawbtc.log
```
#### Step 2. blocksci hourly preprocessing
```bash
crontab -e
## view log
tail -f hourly_blocksci.log
```

#### Step 3. network_data_part_every_block.py
```bash
tmux a -t 1
```

## Ubuntu (Docker) Specification and Structure 
### storage system structure SBIP Ubuntu(docker) server 
two 
```bash
/dev/md1p1      3.6T  680G  2.8T  20% /data1
/dev/md2p1      3.6T   89M  3.4T   1% /data2
```

### file structure under /root directory
```
/root
│   start_rawbtc.sh # step 1 raw btc data synchronization
│   0920_rawbtc.log # log from step 1
│   hourly_blocksci.log # log from step 2
│   bloksci.config # config from step 2
└───BlockSci # step 2 folder
|
└───blocksci_output # step 2 output folder

/data1
|   
└───data_bitcoin  # step 1 raw btc synchronization folder
```

### config for blocksci preprocess in `/root/bloksci.config`
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