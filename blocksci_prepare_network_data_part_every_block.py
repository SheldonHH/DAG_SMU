#!/usr/bin/env python 
# -*- coding:utf-8 -*-
'''
The function prepare graph data form blocksci.
The graph is used for blcoksci_main.py
tip: 2009-1-4 00:00:00  --> 1230998400
'''

from datetime import datetime
import time
import os
import blocksci
import argparse

addr_type_dict ={'Nonstandard' : blocksci.address_type.nonstandard,
                 'Pay to pubkey' : blocksci.address_type.pubkey,
                 'Pay to pubkey hash' : blocksci.address_type.pubkeyhash,
                 'Multisig Public Key' : blocksci.address_type.multisig_pubkey,
                 'Pay to script hash' : blocksci.address_type.scripthash,
                 'Multisig' : blocksci.address_type.multisig,
                 'Null data' : blocksci.address_type.nulldata,
                 'Pay to witness pubkey hash' : blocksci.address_type.witness_pubkeyhash,
                 'Pay to witness script hash' : blocksci.address_type.witness_scripthash}

parser = argparse.ArgumentParser()
parser.add_argument('--split_index', type=int, default=0, help='0-49')
args = parser.parse_args()

def de_multi_num_adds_and_value(num_adds_list, value_list):
    '''
    This function is a sub-function for graph_data_maker.

    It will delete 0 value first.

    Then It is used to deal with the situation below:
    [A,A,A,B] --> [A,B]
    [1,1,1,2] --> [3,2]

    :param num_adds_list:
    :param value_list:
    :return:
    '''
    # format transfer
    num_adds_list = list(num_adds_list)
    value_list = list(value_list)

    # set result lists
    res_num_adds_list = []
    res_value_list = []


    # de zero value
    tmp_de_zero_num_adds_list = []
    tmp_de_zero_value_list  = []

    for value_index in range(len(value_list)):
        value_item = value_list[value_index]

        if value_item != 0.0:
            tmp_de_zero_value_list.append(value_list[value_index])
            tmp_de_zero_num_adds_list.append(num_adds_list[value_index])

    num_adds_list = tmp_de_zero_num_adds_list
    value_list = tmp_de_zero_value_list

    # de_multi processing
    for num_add_index in range(len(num_adds_list)):
        num_add = num_adds_list[num_add_index]
        if num_add not in res_num_adds_list:
            res_num_adds_list.append(num_add)
            res_value_list.append(value_list[num_add_index])

        else:
            res_add_num_index = res_num_adds_list.index(num_add)
            res_value_list[res_add_num_index] += value_list[num_add_index]

    return res_num_adds_list, res_value_list


def graph_data_maker(blksci_path, save_path, start_blk=0, end_blk=-1):
    '''
    This function load the raw data from Bitcoin client data folder,
    Then convert it into the format used in graph analysis.
    :param raw_btc_data_path:
    :param price_data_path:
    :param save_path:
    :return:
    '''

    # 1. Load chain and number property
    main_blk_chain = blocksci.Blockchain(blksci_path)
    pubkey_num = main_blk_chain.address_count(blocksci.address_type.pubkey)
    blocks_num = main_blk_chain.blocks[-1].height + 1
    print('Currently, we have {} Pubkyes and {} Blocks.'.format(pubkey_num, blocks_num))

    # 2. Loop in whole blocks
    transaction_num = 0
    if end_blk == -1: end_blk=blocks_num
    for block_index in range(start_blk, end_blk):
        if block_index >= blocks_num: break
        if block_index%10000==0: print('block_height is ', block_index)
        coinbase_tx_list = []  # Set coinbase address to -8
        normal_tx_list = []

        # 2.1 Get each block data Framework
        block_item = main_blk_chain.blocks[block_index]
        block_time_stamp = block_item.timestamp

        # 2.2 Loop in whole transactions in the block
        tx_in_block = block_item.txes
        for tx_item_index in range(len(tx_in_block)):
            transaction_num += 1
            tx_item = tx_in_block[tx_item_index]

            # make a list contain tx info
            # 2.2.1 --> for coinbase transaction
            if tx_item.is_coinbase:
                # coinbase tx --> [input_index, output_index, tx_value, timestamp, output_pub_add]
                for tx_item_index in range(tx_item.outputs.address.count):
                    # try:
                    add_num = tx_item.outputs.address.address_num[tx_item_index]
                    add_type = tx_item.outputs.address.raw_type[tx_item_index]
                    addr_cl_name = str(add_num) + str(add_type)
                    # except:
                    #     continue

                    output_value = tx_item.outputs.value[tx_item_index]
                    coinbase_tx_info = [-8, addr_cl_name, output_value, block_time_stamp]
                    coinbase_tx_list.append(coinbase_tx_info)



            # 2.2.2 --> for normal transaction
            else:
                # de multi same adds in input_add_list or output_add_list
                this_tx_input_hash_addr = []
                this_tx_input_value = []
                this_tx_output_hash_addr = []
                this_tx_output_value = []

                for input_index in range(tx_item.inputs.address.count):
                    # try:
                    add_num = tx_item.inputs.address.address_num[input_index]
                    add_type = tx_item.inputs.address.raw_type[input_index]
                    addr_cl_name = str(add_num) + str(add_type)
                    this_tx_input_hash_addr.append(addr_cl_name)

                    addr_input_value = tx_item.inputs.value[input_index]
                    this_tx_input_value.append(addr_input_value)

                    # except:
                    #     continue

                for output_index in range(tx_item.outputs.address.count):
                    # try:
                    add_num = tx_item.outputs.address.address_num[output_index]
                    add_type = tx_item.outputs.address.raw_type[output_index]
                    addr_cl_name = str(add_num) + str(add_type)
                    this_tx_output_hash_addr.append(addr_cl_name)

                    addr_output_value = tx_item.outputs.value[output_index]
                    this_tx_output_value.append(addr_output_value)

                    # except:
                    #     continue

                input_num_adds, input_value = de_multi_num_adds_and_value(this_tx_input_hash_addr,
                                                                          this_tx_input_value)

                output_num_adds, output_value = de_multi_num_adds_and_value(this_tx_output_hash_addr,
                                                                            this_tx_output_value)


                tmp_input_num_add = []
                tmp_input_value = []

                # de-multi same num_add
                for input_num_add_index in range(len(input_num_adds)):
                    input_num_add = input_num_adds[input_num_add_index]

                    # if self transaction
                    if input_num_add in output_num_adds:
                        output_num_add_index = output_num_adds.index(input_num_add)
                        this_input_value = input_value[input_num_add_index]
                        this_output_value = output_value[output_num_add_index]

                        # delete the minor one
                        if this_input_value < this_output_value:
                            output_value[output_num_add_index] = this_output_value - this_input_value

                        elif this_input_value > this_output_value:
                            output_num_adds.__delitem__(output_num_add_index)
                            output_value.__delitem__(output_num_add_index)
                            tmp_input_num_add.append(input_num_add)
                            tmp_input_value.append(this_input_value - this_output_value)

                        else:
                            output_num_adds.__delitem__(output_num_add_index)
                            output_value.__delitem__(output_num_add_index)

                    # if not self transaction
                    else:
                        this_input_value = input_value[input_num_add_index]
                        tmp_input_num_add.append(input_num_add)
                        tmp_input_value.append(this_input_value)

                input_num_adds = tmp_input_num_add
                input_value = tmp_input_value

                # allocate input value ratio according to input and add transaction info
                # normal tx --> [input_str_addr, output_str_addr, tx_value, timestamp]
                total_input_value = sum(input_value)

                for input_num_add_index_ in range(len(input_num_adds)):
                    input_ratio = input_value[input_num_add_index_]/total_input_value

                    total_output_value = sum(output_value)
                    for output_num_add_index_ in range(len(output_num_adds)):
                        output_ratio = output_value[output_num_add_index_]/total_output_value

                        input_num_add = input_num_adds[input_num_add_index_]
                        output_num_add = output_num_adds[output_num_add_index_]


                        output_get_tx_value = output_value[output_num_add_index_] * input_ratio
                        input_give_tx_value = input_value[input_num_add_index_] * output_ratio

                        normal_tx_info = [input_num_add, output_num_add,
                                          input_give_tx_value, output_get_tx_value, block_time_stamp]


                        normal_tx_list.append(normal_tx_info)


        # 2.3 save data for each day
        with open(save_path + 'coinbase_block_height_{}.txt'.format(block_index), 'w') as f:
            for coinbase_tx_item in coinbase_tx_list:
                f.write('{}'.format(coinbase_tx_item) + '\n')

        with open(save_path + 'normal_block_height_{}.txt'.format(block_index), 'w') as f:
            for normal_tx_item in normal_tx_list:
                f.write('{}'.format(normal_tx_item) + '\n')



if __name__ == "__main__":
    # 1. Set raw data path (Blocksci load data from Bitcoin Client)
    external_4T_disk = '/media/user_cl/4T_Disk/BTC_network_project_1/'
    blksci_path = '/home/extra_HDD_2/blocksci_made_data_bk_up_2/btc_config.json'
    save_path = external_4T_disk + 'blocksci_graph_data_part_{}/'.format(args.split_index+1)
    if not os.path.exists(save_path): os.mkdir(save_path)

    # 2. Main processing
    graph_data_maker(blksci_path, save_path, start_blk=0, end_blk=-1)
    print('Processing Finish')
