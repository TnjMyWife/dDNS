# 配置步骤

### 1.安装protobuf编译器和[grpc](https://so.csdn.net/so/search?q=grpc&spm=1001.2101.3001.7020)库

```bash
pip install grpcio-tools
```

### 2.编译.protoc文件生成.py文件

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. dDNS.proto
```

生成如下两个rpc调用代码模块：
`dDNS_pb2.py` 保存protoc文件中定义的message生成的python类
`dDNS_pb2_grpc.py` 保存protoc文件中定义的服务类型生成的RPC方法

### 3.启动

客户端：

```bash
python .\ddnsClient.py
```

服务器:

```bash
python .\ddnsServer.py
```

