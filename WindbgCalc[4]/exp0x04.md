## 通过调试器监控计算器运行，每当运行结果为666时输出999

### 实验环境

- windows7

### 实验工具

- windbg
- calc.exe

### 实验过程

- 通过分析和对SetWindowText下断点观察esp中的内容确定需要提取的输出内容在```esp+8```

- 新建txt文件，输入如下脚本

  ```
  # as 创建别名
  # /mu 参数指定的内存地址当作unicode
  # poi 指针中的数据
  as /mu ${/v:name} poi(esp+0x8)  
  
  # .if .else条件判断
  # $scmp比较字符串是否相等
  
  .if($scmp(@"${name}","666")==0){ezu poi(esp+0x8) "999";}.else{.echo ${name};}
  
  #run
  g
  ```

- 在windbg的command中输入```bp SetWindowTextW "$>dbg.txt"```

### 实验结果

​	![](result.gif)



### 实验问题

- 实验只是将输出改为999，并不是只对运算结果中的666改为999

### 参考资料

- [e--ea--eb--ed--ed--ef--ep--eq--eu--ew--eza--ezu--enter-values-](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/e--ea--eb--ed--ed--ef--ep--eq--eu--ew--eza--ezu--enter-values-)
- [SoftSecurity_job](https://github.com/jackcily/SoftSecurity_job/blob/master/job4.md)
- [windbg 脚本简单入门](https://bbs.pediy.com/thread-180879.htm)