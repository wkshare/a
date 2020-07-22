#!/usr/bin/python
#author:wangkai
#date:2016-05-26 modify

#0: normal
#1:mysql server runing
#2:mysql subordinate not runing 
#3:mysql connecting mysql error,check mysql user or password.

import os
import sys
import commands
import subprocess
import socket


hostname = socket.gethostname()


keys = [
    "com_insert",
    "com_delete",
    "com_update",
    "com_select",

    "questions",
    "com_commit",
    "com_rollback",

    "threads_cached",
    "threads_connected",
    "threads_created",
    "threads_running",
    "connections",

    "innodb_buffer_pool_read_requests",
    "innodb_buffer_pool_read_ahead",
    "innodb_buffer_pool_reads",

    "created_tmp_disk_tables",
    "created_tmp_files",
    "created_tmp_tables",

    "binlog_cache_disk_use",
    "binlog_cache_use",

    "innodb_log_waits",
    "innodb_buffer_pool_wait_free",
    "handler_read_first",
    "handler_read_key",
    "handler_read_next",
    "handler_read_prev",
    "handler_read_rnd",
    "handler_read_rnd_next",

    "select_full_join",
    "select_range",
    "select_range_check",
    "sort_merge_passes",

    "slow_queries",

    "table_locks_immediate",
    "table_locks_waited"
]


subordinate_keys = [
    "subordinate_io_running",
    "seconds_behind_main",
    "subordinate_sql_running"
]


def check_stdout(cmd):
    try:
        data = subprocess.check_output(cmd, shell=True, stderr=open(os.devnull, 'w'), universal_newlines=True)
        status = 0
    except subprocess.CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data

def mysql_instance():
    # cmd = "netstat -ntlp|grep 'mysqld'|awk '{print $4}'")
    # high performane if network sockets high
    cmd = """ss -nltp | grep '"mysqld"' | awk '{print $4}'"""
    mysqld_status,command_result  = commands.getstatusoutput(cmd)
    if mysqld_status != 0 or len(command_result) == 0:
        sys.exit(1)
    if "\n" in command_result:
        mysql_instance = command_result.split('\n')
    else:
        mysql_instance = []
        mysql_instance.append(command_result)
    mysql_listen = []
    for i in mysql_instance:
        mysql_listen_ip = i.split(':')[0]
        if mysql_listen_ip == '0.0.0.0' or mysql_listen_ip == '' or mysql_listen_ip == '*':
            mysql_listen_ip = '127.0.0.1'
        mysql_listen_port = i.split(':')[-1]
        if mysql_listen_port == "4567":
            # ignore Percona Xtradb Cluster group communication port
            continue
        mysql_status(mysql_listen_ip,mysql_listen_port,keys)
        mysql_status_subordinate(mysql_listen_ip,mysql_listen_port,subordinate_keys)


def mysql_status_subordinate(ip,port,subordinate_keys):
    mysql_command = 'mysql -h %s -P %s -uzabbix -p4rfvQcos -e "show subordinate status;"' % (ip, port)
    mysql_status,command_result = check_stdout(mysql_command)
    if mysql_status != 0 or len(command_result) == 0:
        print "mysql_status{mysql_host=\"%s:%s\",type=\"subordinate_status\"} 2" % (hostname, port)
        return
    else:
        print "mysql_status{mysql_host=\"%s:%s\",type=\"subordinate_status\"} 0" % (hostname, port)
        result_list = command_result.split('\n')
        result_list_lower = [j.lower() for j in result_list]
        result_list_lower_tmp = [ i.split('\t') for i in result_list_lower ]
        result_dict = dict(zip(result_list_lower_tmp[0],result_list_lower_tmp[1]))
        for k in subordinate_keys:
            if result_dict.has_key(k):
                if result_dict[k] == 'yes':
                    ret_k = 1
                elif result_dict[k] == 'no':
                    ret_k = -1
                else:
                    ret_k = result_dict[k]
                print "mysql_status{mysql_host=\"%s:%s\",type=\"%s\"} %s" % (hostname, port,k,ret_k)
 

def mysql_status(ip,port,keys):
    mysql_command = 'mysql -h %s -P %s -uzabbix -p4rfvQcos -e "show global status;"' % (ip, port)
    mysql_status,command_result = check_stdout(mysql_command)
    if mysql_status != 0 or len(command_result) == 0:
        print "mysql_status{mysql_host=\"%s:%s\",type=\"mysql_status\"} 3" % (hostname, port)
        return
    else:
        print "mysql_status{mysql_host=\"%s:%s\",type=\"mysql_status\"} 1" % (hostname, port)
        result_list = command_result.split('\n')
        result_list_lower = [j.lower() for j in result_list]
        result_list_lower_tmp = [ i.split('\t') for i in result_list_lower ]
        result_dict = dict(result_list_lower_tmp)
        for k in keys:
            if result_dict.has_key(k):
                print "mysql_status{mysql_host=\"%s:%s\",type=\"%s\"} %s" % (hostname, port, k, result_dict[k])

mysql_instance()
