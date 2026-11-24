#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/wifi-module.h"
#include <iostream>
#include <cstring>

using namespace ns3;

// --- 全局统计变量 ---
uint32_t g_txCount = 0;
uint32_t g_rxCount = 0;
double g_totalDelay = 0.0;
double g_totalNetworkDelay = 0.0; 

// --- 动态全局参数 ---
uint32_t g_kValue = 31;                 // 默认 K=31
uint32_t g_mValue = 6;                  // 默认 M=6
uint32_t g_payloadSize = 207;           // Bytes (114 + 3*13 = 153 Bytes)
double g_verifDelay = 2.65e-6;          // 秒 ((4+2)*0.3317 us = 1.99 us)
uint32_t g_bgNodesCount = 14;           // 背景竞争节点数量 (代表交通密度)
uint32_t g_platoonFollowers = 5;        // 编队跟随车数量 N_PF (默认 5, 支持 2-10 动态调整)

void SendPacket(Ptr<Socket> socket) {
    uint8_t* buffer = new uint8_t[g_payloadSize];
    memset(buffer, 0, g_payloadSize);
    double txTime = Simulator::Now().GetSeconds();
    memcpy(buffer, &txTime, sizeof(txTime));
    
    Ptr<Packet> packet = Create<Packet>(buffer, g_payloadSize);
    socket->Send(packet);
    g_txCount++;
    delete[] buffer;
    
    // 领航车以 10 Hz 频率发送控制命令
    Simulator::Schedule(Seconds(0.1), &SendPacket, socket);
}

void ReceivePacket(Ptr<Socket> socket) {
    Ptr<Packet> packet;
    while ((packet = socket->Recv())) {
        uint8_t buffer[8];
        packet->CopyData(buffer, 8);
        double txTime;
        memcpy(&txTime, buffer, 8);
        double rxTime = Simulator::Now().GetSeconds();
        
        double netDelay = rxTime - txTime;
        g_totalNetworkDelay += netDelay;

        // E2E时延 = 物理网络传播延时 + TPM 验证延时
        double e2eDelay = netDelay + g_verifDelay;
        g_totalDelay += e2eDelay;
        g_rxCount++;
    }
}

int main(int argc, char *argv[]) {
    CommandLine cmd;
    cmd.AddValue("K", "Global secret share pool size (K)", g_kValue);
    cmd.AddValue("M", "Local secret share subset size (M)", g_mValue);
    cmd.AddValue("followers", "Number of platoon followers N_PF (2-10)", g_platoonFollowers);
    cmd.AddValue("bgNodes", "Number of background traffic nodes (Density)", g_bgNodesCount);
    cmd.Parse(argc, argv);

    // |Msg|(10B) + |i|(4B) + |t|(4B) + 3*lambda(96B) + K*|MAC|(3B*K) = 114 + 3*K
    g_payloadSize = 114 + 3 * g_kValue;
    
    // 单车 TPM 局部份额延迟 = (M + 2) * Thash(0.3317 us)
    g_verifDelay = (g_mValue + 2) * 0.3317 * 1e-6;

    uint32_t totalNodes = (g_platoonFollowers + 1) + g_bgNodesCount;
    NodeContainer nodes;
    nodes.Create(totalNodes);

    std::string traceFile = "/home/pianochip/simulation/sumo_scenario/ns2mobility.tcl";
    Ns2MobilityHelper ns2 = Ns2MobilityHelper(traceFile);
    ns2.Install();

    // 配置 IEEE 802.11p (WAVE) 标准
    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211p);
    
    wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                 "DataMode", StringValue("OfdmRate6MbpsBW10MHz"),
                                 "ControlMode", StringValue("OfdmRate6MbpsBW10MHz"),
                                 "NonUnicastMode", StringValue("OfdmRate6MbpsBW10MHz"));

    YansWifiPhyHelper wifiPhy;
    wifiPhy.Set("TxGain", DoubleValue(2.0)); 
    wifiPhy.Set("RxGain", DoubleValue(2.0));
    wifiPhy.Set("TxPowerStart", DoubleValue(20.0));
    wifiPhy.Set("TxPowerEnd", DoubleValue(20.0));

    YansWifiChannelHelper wifiChannel;
    wifiChannel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel");
    wifiChannel.AddPropagationLoss("ns3::FriisPropagationLossModel");
    wifiChannel.AddPropagationLoss("ns3::NakagamiPropagationLossModel",
                                   "m0", DoubleValue(3.0),
                                   "m1", DoubleValue(2.0),
                                   "m2", DoubleValue(2.0));
    
    wifiPhy.SetChannel(wifiChannel.Create());

    WifiMacHelper wifiMac;
    wifiMac.SetType("ns3::AdhocWifiMac");
    
    NetDeviceContainer devices = wifi.Install(wifiPhy, wifiMac, nodes);

    InternetStackHelper internet;
    internet.Install(nodes);
    Ipv4AddressHelper ipv4;
    ipv4.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer interfaces = ipv4.Assign(devices);

    uint16_t port = 8000;
    
    //绑定跟随车的接收端 Socket
    for (uint32_t i = 1; i <= g_platoonFollowers; ++i) {
        Ptr<Socket> recvSink = Socket::CreateSocket(nodes.Get(i), TypeId::LookupByName("ns3::UdpSocketFactory"));
        InetSocketAddress local = InetSocketAddress(Ipv4Address::GetAny(), port);
        recvSink->Bind(local);
        recvSink->SetRecvCallback(MakeCallback(&ReceivePacket));
    }

    // 绑定领航车发送端
    Ptr<Socket> sourceSocket = Socket::CreateSocket(nodes.Get(0), TypeId::LookupByName("ns3::UdpSocketFactory"));
    sourceSocket->SetAllowBroadcast(true);
    InetSocketAddress remote = InetSocketAddress(Ipv4Address("255.255.255.255"), port);
    sourceSocket->Connect(remote);

    Simulator::Schedule(Seconds(15.0), &SendPacket, sourceSocket);
    Simulator::Stop(Seconds(50.0));

    std::cout << "Starting NS-3 LSPA Platooning Simulation..." << std::endl;
    std::cout << "Config -> K: " << g_kValue << ", M: " << g_mValue 
              << " | Followers (N_PF): " << g_platoonFollowers
              << " | Payload: " << g_payloadSize << " Bytes"
              << " | BgNodes: " << g_bgNodesCount << std::endl;
    
    Simulator::Run();
    Simulator::Destroy();

    // 性能指标结算与延迟
    double pdr = (g_txCount > 0) ? ((double)g_rxCount / (g_txCount * g_platoonFollowers)) * 100.0 : 0.0;
    
    double avgE2eDelayMs = (g_rxCount > 0) ? (g_totalDelay / g_rxCount) * 1000.0 : 0.0;
    double avgNetDelayMs = (g_rxCount > 0) ? (g_totalNetworkDelay / g_rxCount) * 1000.0 : 0.0;
    double lspaVerificationMs = g_verifDelay * 1000.0;

    // 根据动态负载大小估算物理发送时间 (6 Mbps 带宽)
    double approxTxDelayMs = ((g_payloadSize + 40) * 8.0) / 6000000.0 * 1000.0; 
    double approxPropDelayMs = 0.0005;

    double queueAndContentionMs = avgNetDelayMs - approxTxDelayMs - approxPropDelayMs;
    if (queueAndContentionMs < 0) queueAndContentionMs = 0.0;

    std::cout << "\n=================================================" << std::endl;
    std::cout << "       LSPA Simulation Results (Dynamic K, M)      " << std::endl;
    std::cout << "=================================================" << std::endl;
    std::cout << "Total Packets Transmitted : " << g_txCount << std::endl;
    std::cout << "Total Packets Received    : " << g_rxCount << std::endl;
    std::cout << "Packet Delivery Ratio     : " << pdr << " %" << std::endl;
    std::cout << "-------------------------------------------------" << std::endl;
    std::cout << "[ E2E Delay Breakdown ]" << std::endl;
    std::cout << "1. Queuing & Contention   : ~" << queueAndContentionMs << " ms" << std::endl;
    std::cout << "2. Transmission Delay     : ~" << approxTxDelayMs << " ms" << std::endl;
    std::cout << "3. Propagation Delay      : ~" << approxPropDelayMs << " ms" << std::endl;
    std::cout << "4. LSPA Verification Delay:  " << lspaVerificationMs << " ms" << std::endl;
    std::cout << "-------------------------------------------------" << std::endl;
    std::cout << "Average E2E Delay (Sum)   : " << avgE2eDelayMs << " ms" << std::endl;
    std::cout << "=================================================\n" << std::endl;

    return 0;
}