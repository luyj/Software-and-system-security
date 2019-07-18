# 端口为7331
@load frameworks/communication/listen
const communication::listen_port = 7331/tcp &redef;

# 注册alert_shellcode事件检测是否有shellcode代码及传输unicorn的有效负载
const communication::nodes += {
    ["mipu"] = [$host = 127.0.0.1,$events = /alert_shellcode/,$connect = F,$ssl = F]
} &redef;

# shellcode签名

export{
    const match_shellcode=/(909090909090909090)|(5c62696e5c7368)|(909090E8C0)|(cd80)|(5831d20f05)|(0f05)/;
    const noneasii = /[^\x00-\x7F]/;
}

# 声明全局事件is_shellcode，unicorn.py接收
global is_shellcode:event(pay:string,do:int);
event alert_shellcode(sc:string,syscall:string,arg1:string,arg2:string)
{
    print "###########################################";
    print "UNICORN DETECTED SHELLCODE";
    print fmt("hey! hey!,Have u been pwned?");
    print fmt("hexpayload: %s",sc);
    print fmt("syscall: %s",syscall);
    print fmt("arg: %s",arg1);
    print "###########################################";
}

event bro_init()
{
    print("Hello from _Mipu!");
}

event connection_SYN_packet(c:connection,pkt:SYN_packet)
{
        print fmt("---------------------------");
        print fmt("new connection from : %s:%s --> %s:%s",c$id$orig_h,c$id$orig_p,c$id$resp_h,c$id$resp_p);
        print fmt("---------------------------");
}


# 对捕获数据进行分析 
event tcp_packet(c: connection, is_orig: bool, flags: string, seq: count, ack: count, len: count, payload: string)
{
    if(payload !=""){
            if(noneasii in payload)
            {
                    payload=bytestring_to_hexstr(payload);
                    print fmt("detected nonascii in payload!!!\n hexpayload : %s \n", payload);
                    if(match_shellcode in payload){
                            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$";
                            print "$$$$ BRO DETECTED SHELLCODE $$$$$";
                            print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$";
                    }
                    else
                    {
                            event is_shellcode(payload,1);
                    }                }
            else{
            print fmt("payload: %s",payload);
            }
    }
}
