import time
import grpc
from copy import deepcopy
from concurrent import futures
from dDNS_pb2 import FORDATA, DATA, NULL, ID, DATASET, TOPRE, TOSUC, ADD, DEL, QUERY, RESP
from dDNS_pb2_grpc import rpcServiceServicer, add_rpcServiceServicer_to_server, rpcServiceStub


allServer = [26000 + j for j in range(16)]    # 预先确定的服务器地址
args = [('grpc.connect_timeout_ms', int(500))]  # 设置超时时间500ms
channels = [grpc.insecure_channel('localhost:' + str(port), options=args) for port in allServer]    # gRPC通道集合
stubs = [rpcServiceStub(channel) for channel in channels]   # 创建gRPC存根

# 哈希函数
def myHash(key):
    v = 0
    for char in key:
        v = (v + ord(char)) % 16
    return v

# 重新建立和特定节点id的RPC连接
def connectBuild(id):
    global channels
    global stubs
    channels[id] = grpc.insecure_channel('localhost:' + str(allServer[id]))
    stubs[id] = rpcServiceStub(channels[id])


# 实现服务器服务功能的类
class dDNS(rpcServiceServicer):
    def __init__(self, port):   # 手动传入端口
        self.localData = {}     # 本地数据字典，从域名映射到(IP，ID)
        self.cacheData = {}     # 缓存数据字典，从域域名映射到(IP，缓存过期时间)
        self.id = int(port) % 26000  # 本节点id，通过哈希端口获得
        self.sucId = self.id    # 后继节点id
        self.preId = self.id    # 前驱节点id
        self.aliveServer = []   # 当前存活服务器

        ''' 向所有服务器发送请求，探测存活的服务器 '''
        print('probing alive servers...')
        for i, stub in enumerate(stubs):
            # 除了自己以外
            if i == self.id:
                continue
            try:
                # 调用存根，向服务器发送请求
                self.aliveServer.append(stub.Ask(ID(id=self.id)).id)
                print(f'proecss {i} is alive')
            except Exception as e:
                print(f'proecss {i} is offline')
                continue
        print(f'currently alive servers: {self.aliveServer}')

        # 从当前存活服务器中找前驱后继
        if self.findPreAndSuc(self.aliveServer, self.id):
            print(f"Join the cluster sucessful, my pre: {self.preId}, my suc:{self.sucId}")
            print(f'ask for data...')
            # 调用存根，向后继要数据，并保存在本地
            dataSet = stubs[self.sucId].AskForData(FORDATA(preId=self.preId, id=self.id))
            for data in dataSet.dataset:
                self.localData[data.domain] = (data.ip, data.id)
            print(f'get data:{self.localData}')
        print('-------------------------------------------------\n')

    ''' 从当前存活服务器中找前驱后继 '''
    def findPreAndSuc(self, list, id):
        lowerThan = [num for num in list if num < id]
        greaterThan = [num for num in list if num > id]
        if not lowerThan and not greaterThan:
            return False
        self.preId = max(greaterThan) if not lowerThan else max(lowerThan)     # 如果没有id比自己小的节点，则前继应该为必自己大的节点的最大值
        self.sucId = min(lowerThan) if not greaterThan else min(greaterThan)   # 如果没有id比自己大的节点，则后继继应该为比自己小的节点的最小值
        return True

    # 加入---向所有服务器发请求， 其他服务器以自身id进行响应
    def Ask(self, request, context):
        print('-------------------------------------------------')
        self.aliveServer.append(request.id)
        print(f'process {request.id} join !!!')
        # 重新寻找前驱后继
        self.findPreAndSuc(self.aliveServer, self.id)
        print(f'my new suc: {self.sucId}')
        print(f'my new pre: {self.preId}')
        print(f'Alive Server: {self.aliveServer}')
        # 重新建立grpc连接
        connectBuild(request.id)
        print('-------------------------------------------------\n')
        return ID(id=self.id)

    # 加入---向后继服务器发请求，请求前驱id到自身id的部分数据
    def AskForData(self, request, context):
        print('-------------------------------------------------')
        dataSet = []
        preId = request.preId
        requestId = request.id
        tmp = deepcopy(self.localData)
        print(f'process {requestId} ask for data')
        # 前驱比自己小的情况
        if preId < requestId:
            for domain in tmp:
                if preId < tmp[domain][1] <= requestId:
                    dataSet.append(DATA(domain=domain, ip=tmp[domain][0], id=tmp[domain][1]))
                    del self.localData[domain]
        # 前驱比自己大的情况
        if preId > requestId:
            for domain in tmp:
                if preId < tmp[domain][1] <= 15 or 0 <= tmp[domain][1] <= requestId:
                    dataSet.append(DATA(domain=domain, ip=tmp[domain][0], id=tmp[domain][1]))
                    del self.localData[domain]

        print(f'Data distribution successful!')
        print(f'Before distribution: {tmp}')
        print(f'After distribution: {self.localData}')
        print('-------------------------------------------------\n')
        return DATASET(dataset=dataSet)

    # 退出---告诉前驱服务器我的后继，前驱服务器修改自己的后继
    def ToPre(self, request, context):
        print('-------------------------------------------------')
        print(f"My successor quit, change my successor from {self.sucId} to {request.mysuc}")
        self.sucId = request.mysuc
        print('-------------------------------------------------\n')
        return NULL(null=0)

    # 退出---告诉后继服务器我的前驱，后继服务器修改自己的前驱，并继承数据
    def ToSuc(self, request, context):
        print('-------------------------------------------------')
        print(f"My predecessor quit, change my predecessor from {self.preId} to {request.mypre}")
        print(f"Before reception: {self.localData}")
        self.preId = request.mypre
        for data in request.dataset:
            self.localData[data.domain] = (data.ip, data.id)
        print(f"After reception: {self.localData}")
        print('-------------------------------------------------\n')
        return NULL(null=0)

    # 退出---广播给所有节点，让它们修改自己的存活表
    def Quit(self, request, context):
        print('-------------------------------------------------')
        self.aliveServer.remove(request.id)
        print(f"Multicast: Node {request.id} is quit")
        print(f"Alive Server: {self.aliveServer}")
        print('-------------------------------------------------\n')
        return NULL(null=0)

    # 添加域名请求
    def Add(self, request, context):
        print('-------------------------------------------------')
        print('Client requests to add data')
        domain = request.domain
        ip = request.ip
        domainId = myHash(domain)          # 对域名进行哈希，得到数据项ID
        # 判断域名是否归本结点管理
        if ((self.preId < self.id and self.preId < domainId <= self.id) or
            (self.preId > self.id and (self.preId < domainId <= 15 or 0 <= domainId <= self.id)) or
            (self.preId == self.id)):
            self.localData[domain] = (ip, domainId)     # 向本地添加数据
            print(f'current server data:{self.localData}')
            print('-------------------------------------------------\n')
            return RESP(err=False, response="添加域名成功，服务器 %d " % self.id)
        else:
            # 不属于本节点维护，转发给下一个节点
            print('Data ID does not belong to me, Forward to the next servers')
            print('-------------------------------------------------\n')
            return stubs[self.sucId].Add(request)

    # 删除数据的请求
    def Remove(self, request, context):
        print('-------------------------------------------------')
        print('Client requests to remove data')
        domain = request.domain
        domainId = myHash(domain)  # 对域名进行哈希，得到数据项ID
        # 判断域名是否归本结点管理
        if ((self.preId < self.id and self.preId < domainId <= self.id) or
            (self.preId > self.id and (self.preId < domainId <= 15 or 0 <= domainId <= self.id)) or
            (self.preId == self.id)):
            try:
                del self.localData[domain]      # 移除相应域名项
            except Exception as e:
                return RESP(err=True, response="域名 %s 不存在，无法解析" % domain)
            else:
                print("Remove successful")
                print(f'current server data:{self.localData}')
                print('-------------------------------------------------\n')
                return RESP(err=False, response="从服务器 %d 删除数据成功" % self.id)
        else:
            # 不属于本节点维护，转发给下一个节点
            print('Data ID does not belong to me, Forward to the next servers')
            print('-------------------------------------------------\n')
            return stubs[self.sucId].Remove(request)

    # 修改数据的请求
    def Modify(self, request, context):
        print('---------------------------------------------------------------------------------')
        print('Client requests to modify data')
        oldDomain = request.oldDomain       # 原域名
        newDomain = request.newDomain       # 新域名
        newIp = request.newIp       # 新IP
        # 删除旧域名
        server1 = stubs[self.id].Remove(DEL(domain=oldDomain))
        if server1.err:
            return server1
        # 添加新域名
        server2 = stubs[self.id].Add(ADD(domain=newDomain, ip=newIp))
        print('---------------------------------------------------------------------------------\n')
        return RESP(err=False, response=server1.response + "\t" + server2.response)

    def Query(self, request, context):
        print('-------------------------------------------------')
        print('Client requests to query data')
        domain = request.domain
        print("Search in cache")
        # 从缓存中寻找数据
        if domain in self.cacheData.keys():
            temp = self.cacheData[domain]   # 获取缓存数据
            # 判断缓存是否过期
            if time.time() <= temp[1]:
                print("Cache hit!")
                print('-------------------------------------------------\n')
                return RESP(err=False, response=temp[0])
            # 如果缓存过期，则删除缓存数据
            else:
                del self.cacheData[domain]
        print("cache miss or cache expired")

        domainId = myHash(domain)        # 对域名进行哈希得到数据项Id
        # 判断域名是否归本结点管理
        if ((self.preId < self.id and self.preId < domainId <= self.id) or
            (self.preId > self.id and (self.preId < domainId <= 15 or 0 <= domainId <= self.id)) or
            (self.preId == self.id)):
            print('Data ID belong to me')
            # 判断域名是否存在
            if domain in self.localData.keys():
                # 域名存在，向缓存中添加并返回
                print("Data found")
                self.cacheData[domain] = (self.localData[domain][0], time.time() + 30)		# 保存在缓存中，设定超时时间为30s
                print('-------------------------------------------------\n')
                return RESP(err=False, response=self.localData[domain][0])
            else:
                # 域名不存在，返回错误信息
                print("No data in local data")
                print('-------------------------------------------------\n')
                return RESP(err=True, response="域名 %s 不存在，无法解析" % domain)
        else:
            # 不属于本节点维护，转发给下一个节点
            print(f'Data ID does not belong to me, Forward to the next servers {self.sucId}')
            print("Wating for other servers' response...")
            response = stubs[self.sucId].Query(QUERY(domain=domain))
            # 得到正确数据项后，放入本地缓存中，并返回
            if not response.err:
                ip = response.response
                self.cacheData[domain] = (ip, time.time() + 30)		# 保存在缓存中，设定超时时间为30s
            print('-------------------------------------------------\n')
            return response

    def __del__(self):
        print("Preparing to leave the cluster")
        # 集群还有别的节点，需要告知
        if self.preId != self.id:
            # 向存活服务器节点广播退出信息
            print("Boardcasting...")
            for id in self.aliveServer:
                try:
                    stubs[id].Quit(ID(id=self.id))
                except Exception as e:
                    continue
            # 向前驱发送离开信息
            print(f"Sending departure messages to the my suc:{self.sucId} and my pre:{self.preId}")
            stubs[self.preId].ToPre(TOPRE(mysuc=self.sucId))
            dataSet = []
            for domain in self.localData:
                dataSet.append(DATA(domain=domain, ip=self.localData[domain][0], id=self.localData[domain][1]))
            # 向后继发送离开信息和数据
            stubs[self.sucId].ToSuc(TOSUC(mypre=self.preId, dataset=dataSet))





def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=16))        # 创建线程池支持最多16个连接
    port = input("Enter the server port you want: ")
    add_rpcServiceServicer_to_server(dDNS(port), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    while True:
        user_input = input("Type 'quit' to exit: \n")
        if user_input.lower() == 'quit':
            print("Exiting...")
            server.stop(1)
            break


if __name__ == '__main__':
    serve()
