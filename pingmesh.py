#coding=utf-8
from flask import render_template,jsonify,request
from flask import Flask
from config import hosts, password, username, mesh_data
import time
import random
import re
import os
import threading
app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    hosts_ = []
    for i,host in enumerate(hosts):
        index = str(i)
        name = 'host'+index.rjust(2, '0')
        hosts_.append(name)
    return render_template("index.html", **locals())


@app.route('/update_mesh/')
def update_mesh():
    # print(mesh_data)
    #此处数据只为展示，最好用数据库保存历史数据，以便查看
    return jsonify(mesh_data)

def start_thread():
    # 线程数视具体情况而定
    for i, host in enumerate(hosts):
        th = threading.Thread(target=popen_ping, args=(i,))
        th.start()

def popen_ping(i):
    s_ip = hosts[i]
    while True:
        for j in range(len(hosts)):
            r_ip = hosts[j]
            key = 'host'+str(i).rjust(2, '0')+'-'+'host'+str(j).rjust(2, '0')
            cmd = "sshpass -p '{0}' ssh {1}@{2} 'ping -q -c 4 -i 0.2 -w 1 {3}'".format(password, username, s_ip, r_ip)
            r = os.popen(cmd).read().replace('\n', '')
            res = re.match('.+received, (\d+)% packet loss, time (.*)rtt min/avg/max/mdev = (.*) ms',r).groups()
            #丢包率, 4次ping总耗时, 平均响应时间
            packet_loss, total_time, avg_time = res[0], res[1], res[2].split('/')[1]
            #平均响应时间以0-10ms为基准,换算成百分制(视情况而定，此处延迟都较小，为了页面便于区分故×10)
            value = int(float(avg_time)*10)
            title = '丢包率:'+packet_loss+'%，4次ping总耗时:'+total_time+'，平均响应时间:'+avg_time+'ms.'
            mesh_data[key] = [value, title]
        time.sleep(5)


if __name__ == '__main__':
    start_thread()
    app.run(host='0.0.0.0',port=8000)

