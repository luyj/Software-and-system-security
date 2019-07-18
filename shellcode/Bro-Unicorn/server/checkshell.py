from __future__ import print_function
from broccoli import *
from unicorn import *
from unicorn.x86_const import *

ADDRESS = 0x1000000

global bc,payload
payload = ""

# Uc事例句柄，指令长度，执行长度，用户自定义数据
# hook_code在执行每一条语句的时候都会被调用
def hook_code(uc,address,size,data):
    print(">>> Tracing instruction at 0x%X,instruction size = 0x%x"%(address,size))
    
    # 从内存中读取指令
    tmp = uc.mem_read(address,size)
    print(">>> Instruction code at [0x%x]"%(address),end="")
    for i in tmp:
        print("%0x2x"%i,end="")
    print("")

# 回调跟踪基本块
def hook_block(uc,into,data):
   print(">>> Tracing basic block at 0x%x, block size = 0x%x" %(address, size))

def hook_intr(uc,intno,data):
    global payload
    if intno != 0x80:
        uc.emu_stop()
        return
    eax = uc.reg_read(UC_X86_REG_EAX)
    eip = uc.reg_read(UC_X86_REG_EIP)
    esp = uc.reg_read(UC_X86_REG_ESP)

    
    # https://www.tutorialspoint.com/assembly_programming/assembly_system_calls
    # 所有系统调用都列在/usr/include/asm/unistd.h中,在调用int 80h之前放在EAX中的值
    if eax == 1: # system call number (sys_exit)
        print(">>> 0x%x: interrupt 0x%x, EAX = 0x%x" %(eip, intno, eax))
    elif eax == 4: # system call number (sys_write)
        # 读取ECX,EDX值
        ecx = uc.reg_read(UC_X86_REG_ECX)
        edx = uc.reg_read(UC_X86_REG_EDX)

        try:
            buf = uc.mem_read(eax,edx)
            print(">>> 0x%x: interrupt 0x%x, SYS_WRITE. buffer = 0x%x, size = %u, content = " \
                                                %(eip, intno, ecx, edx), end="")
            for i in buf:
                print("%c"%i,end="")
            print("")
        except UcError as e:
            print(">>> 0x%x: interrupt 0x%x, SYS_WRITE. buffer = 0x%x, size = %u, content = <unknown>\n" \
                                                %(eip, intno, ecx, edx))
    elif eax == 0xb: # system call number (sys_execv)
        ecx = uc.reg_read(UC_X86_REG_ECX)
        edx = uc.reg_read(UC_X86_REG_EDX)
        try:
            buf = uc.mem_read(esp,8)
            print(">>> 0x%x:interrupt 0x%x,SYS_EXECVE.Content = "%(eip,intno),end="")
            for i in buf:
                print("%c"%i,end="")
        except UcError as e:
            print(">>> 0x%x: interrupt 0x%x, SYS_EXECVE.Content = <unknown>\n" \
                                                %(eip, intno)) 
    else:
        print(">>> 0x%x: interrupt 0x%x, EAX = 0x%x" %(eip, intno, eax))

def hook_syscall(mu,data):
    global payload
    
    rax = mu.reg_read(UC_X86_REG_RAX)
    rdi = mu.reg_read(UC_X86_REG_RDI)
    rip = mu.reg_read(UC_X86_REG_RIP)

    if rax == 0x3b: # system call number(sys_execv)
        try:
            buf = mu.mem_read(rdi,8)
            s=""
            for i in buf:
                s+=chr(i)
            print(s)
            k = ">>> 0x%x: interrupt 0x%x, SYS_EXECVE .argument =%s"%(rip, rax,s)
            print (k)
            bc.send("alert_shellcode",string(payload),string("SYS_EXECVE"),string(s),string(""))
        except UcError as e:
            k = ">>> 0x%x: interrupt 0x%x .argument =unknow"%(rip, rax)
            return k
    else:
        k = ">>> 0x%x: interrupt 0x%x"%(rip, rax)
    print(k)
    return k
    mu.emu_stop()




def test_i386(mode,code):
    try:
        # 初始化模拟器
        mu = Uc(UC_ARCH_X86,mode)

        # 内存映射
        mu.mem_map(ADDRESS,2*1024*1024)

        # 加载机器码到模拟器内存空间
        mu.mem_write(ADDRESS,code)

        # 初始化栈,设置栈顶指针
        mu.reg_write(UC_X86_REG_ESP,ADDRESS+0x200000)

        # 处理中断函数,UC_HOOK_INTR 中断，不包括系统调用
        mu.hook_add(UC_HOOK_INTR,hook_intr)

        # 处理系统调用 UC_HOOK_INSN
        # UC_X86_INS_SYSCALL x86指令
        mu.hook_add(UC_HOOK_INSN,hook_syscall,code,1,0,UC_X86_INS_SYSCALL)

        mu.emu_start(ADDRESS,ADDRESS+len(code))

    except UcError as e:
        print("ERROR:%s"%e)

def check_shell(sc):
    test_i386(UC_MODE_64,sc)


###########BRO############################
@event
def is_shellcode(input,do):
    global payload
    print("Input:%s",input)
    payload = input.decode("hex")
    check_shell(payload)
    print("sent")

bc = Connection("127.0.0.1:7331")
while True:
    bc.processInput()