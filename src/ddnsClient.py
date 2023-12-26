import grpc
import time
from dDNS_pb2 import ADD, DEL, MODIFY, QUERY
from dDNS_pb2_grpc import rpcServiceStub


allServer = [26000 + j for j in range(16)]    # 预先确定的服务器地址
args = [('grpc.connect_timeout_ms', int(500))]      # 设置超时时间500ms
channels = [grpc.insecure_channel('localhost:' + str(port), options=args) for port in allServer]    # gRPC通道集合
stubs = [rpcServiceStub(channel) for channel in channels]   # 创建gRPC存根


def connectBuild():
    global channels
    global stubs
    channels = [grpc.insecure_channel('localhost:' + str(i)) for i in allServer]
    stubs = [rpcServiceStub(c) for c in channels]


# 请求添加
def addDomain():
    # 客户输入新增域名和对应的Ip
    domain, ip = input("\nInput message\ndomain_name\tip_address\n").split()
    request = ADD(domain=domain, ip=ip)         # 创建请求信息
    # 调用存根发送添加请求，服务器选择上选择对所有服务器进行请求
    for stub in stubs:
        try:
            response = stub.Add(request)
        except Exception as e:
            continue
        else:
            # 输出服务器返回的消息
            print(response.response)
            return
    print("服务器集群未启动或故障，请稍候重试")


# 请求删除
def rmDomain():
    # 创建消息Req_Remove，指定要删除的数据
    domain = input("\nInput message\ndomain_name\n")
    request = DEL(domain=domain)
    # 通过存根传递删除请求，轮询直到一个服务器响应，并接受服务器返回的消息
    for stub in stubs:
        try:
            response = stub.Remove(request)
        except Exception as e:
            continue
        else:
            # 输出服务器返回的消息
            print(response.response)
            return
    print("服务器集群未启动或故障，请稍候重试")


# 请求修改
def modifyDomain():
    # 创建消息Req_Modify，指定要修改的数据
    oldDomain, newDomain, newIp = input(
        "\nInput message\nold_domain_name\tnew_domain_name\tnew_ip_address\n"
    ).split()
    request = MODIFY(oldDomain=oldDomain, newDomain=newDomain, newIp=newIp)
    # 通过存根传递修改请求，轮询直到一个服务器响应，并接受服务器返回的消息
    for stub in stubs:
        try:
            response = stub.Modify(request)
        except Exception as e:
            continue
        else:
            # 输出服务器返回的消息
            print(response.response)
            return
    print("服务器集群未启动或故障，请稍候重试")


# 请求查询
def queryDomain():
    # 创建消息Req_Query，指定要查询的数据
    domain = input("\nInput message\ndomain_name\n")
    request = QUERY(domain=domain)
    for stub in stubs:
        try:
            response = stub.Query(request)
        except Exception as e:
            continue
        else:
            # 输出服务器返回的消息
            print(response.response)
            return
    print("服务器集群未启动或故障，请稍候重试")


if __name__ == '__main__':
    connectBuild()
    while True:
        print("-----------------------------------------------------------")
        print("请选择请求类型：")
        print("1:域名新增")
        print("2:域名删除")
        print("3:域名更改")
        print("4:域名解析")
        choice = int(input())
        if choice == 1:
            start_time = time.time()
            addDomain()
            end_time = time.time()
            print(f'执行时间:{end_time - start_time}s')
        elif choice == 2:
            start_time = time.time()
            rmDomain()
            end_time = time.time()
            print(f'执行时间:{end_time - start_time}s')
        elif choice == 3:
            start_time = time.time()
            modifyDomain()
            end_time = time.time()
            print(f'执行时间:{end_time - start_time}s')
        elif choice == 4:
            start_time = time.time()
            queryDomain()
            end_time = time.time()
            print(f'执行时间:{end_time - start_time}s')
        connectBuild()
        print("-----------------------------------------------------------\n")
