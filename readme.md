# 请求调页存储管理方式模拟

## 1 项目背景

### 1.1 页式管理机制

​	页式存储管理将程序逻辑地址空间划分为固定大小的页(page)，而物理内存划分为同样大小的页框(page frame)。每一个作业有一个页表，用来记录各个页在内存中所对应的块（页框）。

​	请求分页存储管理建立在基本分页系统基础之上，为了支持虚拟存储器功能而增加了请求调页功能和页面置换功能。请求分页是目前最常用的一种实现虚拟存储器的方法。在请求分页系统中，只要求将当前需要的一部分页面装入内存，便可以启动作业运行。在作业执行过程中，当所要访问的页面不在内存时，再通过调页功能将其调入，同时还可以通过置换功能将暂时不用的页面换出到外存上，以便腾出内存空间。

### 1.2 项目需求

​	编写一个程序，模拟请求调页存储管理方式，一共有320条指令，假设每个页面可以存放10条指令，分配的作业有4个内存块，模拟该作业的执行过程，采用FIFO算法或LRU算法来实现置换。

### 1.3 项目目的

- 理解操作系统执行页面置换的过程
- 加深对FIFO，LRU等算法的理解

## 2 需求分析

### 2.1 基本需求

​	本项目的基本情况如下：

- 指令：共320条指令

- 页面：每个页面存放10条指令，即有32个页
- 内存：该作业的内存块有4块
- 指令分布：

  - 50%顺序执行
  - 25%均匀分布在前地址部分
  - 25%均匀分布在后地址部分
- 置换算法：`FIFO`或`LRU`

### 2.2 模拟过程

  按照需求设计程序模拟请求调页存储管理方式：

- 在模拟过程中：

  - 如果所访问指令在内存中，则显示其物理地址，并转到下一条指令
  - 如果没有在内存中，则发生缺页，此时需要记录缺页次数，并将其调入内存
  - 如果4个内存块中已装入作业，则需进行页面置换
- 所有320条指令执行完成后，计算并显示作业执行过程中发生的缺页率 
- 置换算法可以选用FIFO或者LRU算法 

### 2.3 指令访问次序（参考）

1. 在0－319条指令之间，随机选取一个起始执行指令，如序号为m
2. 顺序执行下一条指令，即序号为m+1的指令
3. 通过随机数，跳转到前地址部分0－m-1中的某个指令处，其序号为m1
4. 顺序执行下一条指令，即序号为m1+1的指令
5. 通过随机数，跳转到后地址部分m1+2 - 319中的某条指令处，其序号为m2
6. 顺序执行下一条指令，即m2+1处的指令。
7. 重复跳转到前地址部分、顺序执行、跳转到后地址部分、顺序执行的过程，直到执行完320条指令。

## 3 设计方案

### 3.1 模拟流程

1. 程序每一步模拟时，首先从指令序列中获取下一条指令的逻辑地址

2. 根据指令的逻辑地址计算出指令所在的页号

3. 如果指令所在页已调入内存中，则不需换页，更新相关信息（访问时间等）即可；

   否则需要换页，执行页面调度算法计算应被换掉的页面

### 3.2 FIFO算法

​	FIFO算法即先进先出算法，即当发生页面置换的时候，最先进入的页最先调出，为了实现FIFO算法，我们对每一个内存块增加辅助变量`fresh_time`，用于记录页面更新时间

算法基本流程如下

1. 寻找最早换入的页
2. 将最早换入的页换成新页
3. 更新换页时间

### 3.3 LRU算法

​	LRU算法即最近最久未使用算法，即当发生页面置换的时候，将最长时间没有使用的页调出，我们同样使用辅助变量`access_time`来记录访问的时间

算法基本流程如下

1. 寻找最早访问的页
2. 将最早访问的页换成新页
3. 更新访问时间

## 4 核心代码

### 4.1 数据表示

```python
class MainForm(QtWidgets.QWidget):
    def __init__(self):
        # ... non-related code ...
        
        # Instruction count
        self.count = 0
        # Time count
        self.clock = 0
        # Page fault count
        self.page_fault = 0
        # Instruction sequence
        self.sequence = SKIP()
        # Page swap policy
        self.swap_policy = self.FIFO
        # Page of the four Blocks
        self.page_nums = [-1, -1, -1, -1]
        # The time this Page was swapped in
        self.fresh_time = [-1, -1, -1, -1]
        # The time this Page was accessed
        self.access_time = [-1, -1, -1, -1]
        
        # ... non-related code ...
```

### 4.2 关键逻辑

#### 4.2.1 单步执行

```python
@QtCore.pyqtSlot()
def on_single_step_clicked(self):
    if self.count >= 320:
        # ...
        return

    index = next(self.sequence) # 下一条指令的地址
    page = index // 10          # 下一条指令所在页

    # ...
    for index in range(len(self.page_nums)):
        if self.page_nums[index] == page:    # 命中
            target = index
            self.access_time[index] = self.clock
            # ...
            break
    else:   # 不命中
        self.page_fault += 1
        target = self.swap_policy(page)  # 换页
        old_page = self.page_nums[target]
        self.swap(target, page)

    # ...
    self.count += 1
    self.clock += 1
```

#### 4.2.2 连续执行

连续执行开关用于快速执行指令，查看结果。实现上是采用一个`Timer`每20 ms执行一次单步操作

```python
@QtCore.pyqtSlot()
def on_consecu_step_clicked(self):
    if self.ui.consecu_step.isChecked():
        self.consecu_timer.start(20)
    else:
        self.consecu_timer.stop()
```

#### 4.2.3 重置


```python
@QtCore.pyqtSlot()
def on_reset_all_clicked(self):
    if self.ui.consecu_step.isChecked():
        self.ui.consecu_step.click()

    for index in range(len(self.page_labels)):
    	# ...
        self.page_nums[index] = -1
        self.fresh_time[index] = -1
        self.access_time[index] = -1
    self.count = 0
    self.clock = 0
    self.page_fault = 0
    # ...
```

### 4.3 序列生成算法

​	指令地址序列通过作为Python语言特性的`generator`来生成，`generator`是一种可中断对象。可以通过简单的语法来构造序列。构造一个`generator`对象就如同普通函数调用，而后每次对生成的`generator`对象调用`next()`函数即可获取下一个值

#### 4.3.1 顺序执行

顺序执行生成器会生成递增的指令地址序列

```python
def SEQU():
    count = 0
    while True:
        yield count
        count = (count + 1) % 320
```

#### 4.3.2 随机执行

随机执行生成器会生成完全随机，位于0到319的指令地址序列

```python
def RAND():
    while True:
        yield random.randint(0, 319)
```

#### 4.3.3 SKIP执行

SKIP生成器会如下规则生成指令地址序列

1. 在0－158之间，随机选取一个作为起始指令地址，设为m
2. 顺序执行下一条指令，即序号为m+1的指令
3. 通过随机数，向后跳转到地址部分161－318之间的某个指令处，设为新的m
4. 顺序执行下一条指令，即序号为m+1的指令
5. 通过随机数，向前跳转到地址部分0 - 158之间的某条指令处，设为新的m
6. 跳转到2

```python
def SKIP():
    m = random.randint(0, 158)
    while True:
        yield m  # down [0,158]
        m += 1
        yield m  # next [1,159]
        m = random.randint(161, 318)
        yield m  # up [161,318]
        m += 1
        yield m  # next [162,319]
        m = random.randint(0, 158)
```

### 4.4 调度算法

#### 4.4.1 FIFO算法

```python
def FIFO(self, new_page):
    replaced = 0
    for i, fresh_time in enumerate(self.fresh_time):
        if fresh_time < self.fresh_time[replaced]:
            replaced = i
    return replaced
```

#### 4.4.2 LRU算法

```python
def LRU(self, new_page):
    replaced = 0
    for i, access_time in enumerate(self.access_time):
        if access_time < self.access_time[replaced]:
            replaced = i
    return replaced
```

#### 4.4.3 页面交换

```python
def swap(self, replaced, new_page):
    return_value = self.page_nums[replaced]
    self.fresh_time[replaced] = self.clock
    self.access_time[replaced] = self.clock
    self.page_nums[replaced] = new_page
	# ... non-related code ...
    return return_value
```

## 5 程序演示

### 5.1 界面说明

![1](.\imgs\1.png)

- 最上方一排为基本信息，页面置换算法选择框和指令执行顺序选择框
- 中间部分为四个内存块的内容页面演示
- 左下方为请求调页信息与结果表格
- 右下角为控制区，可以单步执行或者连续执行或重置

### 5.2 单步执行

![2](.\imgs\2.png)

单步执行后，请求调页信息表格中会新增一条记录，内存页面图示中会用红色高亮当前访问的位置，如果发生换页，将会显示一段换页动画

### 5.3 连续执行

![3](.\imgs\3.png)

### 5.4 重置

![4](.\imgs\4.png)

重置后，请求信息表会被清空，内存中由于没有装入有效页面，将被隐藏

## 6 附录

### 6.1 文件说明

- `gui.py`为程序GUI界面代码
- `PageBlock.py`为程序GUI界面上使用的"内存块"自定义控件
- `Main.py`为程序主要代码，包括调度算法，界面动画效果等

### 6.2 开发环境

- 操作系统：`Windows 10`
- 开发语言：`Python`
- 使用的Python包：`PyQt5`

### 6.3 开发工具

- Python代码：`Vscode`、`PyCharm`
- 界面绘制：`QtDesigner`