import extmem
import random
from math import ceil
from relation import R, S


def generate_data(r, s):
    for i in range(112):
        r.append(R(random.randint(1, 40), random.randint(1, 1000)))

    for i in range(224):
        s.append(S(random.randint(1, 40), random.randint(1, 1000)))


def write_relation(relation, required_blk, addr):
    for i in range(required_blk):
        blk_num = buffer.getNewBlockInBuffer()  # 申请到的缓冲区的索引
        data = []
        for j in range(7):
            data.extend([str(relation[i * 7 + j].first_attr), str(' '), str(relation[i * 7 + j].second_attr),
                         str(' ')])
        data.append(str(addr + 1))
        if i == required_blk - 1:
            data[-1] = str(0)
        buffer.data[blk_num].append(data)
        if not buffer.writeBlockToDisk(addr, blk_num):
            print("写入磁盘文件号 %s 失败" % addr)
            exit()
        addr += 1
    return addr


def write_data(data_set, required_blk, tuple_number, addr):
    number_of_attr = len(data_set[0])  # 关系的属性数
    for i in range(required_blk - 1):
        blk_num = buffer.getNewBlockInBuffer()  # 申请到的缓冲区的索引
        data = []
        for j in range(tuple_number):
            for k in range(number_of_attr):
                data.extend([str(data_set[i * tuple_number + j][k]), str(' ')])
        data.append(str(addr + 1))
        buffer.data[blk_num].append(data)
        if not buffer.writeBlockToDisk(addr, blk_num):
            print("写入磁盘文件号 %s 失败" % addr)
            exit()
        addr += 1

    number_of_written = (required_blk - 1) * tuple_number  # 已经写入磁盘的数据个数
    blk_num = buffer.getNewBlockInBuffer()
    data = []
    for i in range(len(data_set) - number_of_written):
        for j in range(number_of_attr):
            data.extend([str(data_set[number_of_written + i][j]), str(' ')])
    data.append(str(0))
    buffer.data[blk_num].append(data)
    if not buffer.writeBlockToDisk(addr, blk_num):
        print("写入磁盘文件号 %s 失败" % addr)
        exit()
    addr += 1

    return addr


def select(relation, attribute, value, addr):
    if relation != 'R' and relation != 'S':
        print(f"关系{relation}不存在！")
        return addr

    # 确定选择的属性
    if attribute == 'A' or attribute == 'C':
        attr_index = 0
    elif attribute == 'B' or attribute == 'D':
        attr_index = 1
    else:
        print(f"属性{attribute}不存在！")
        return addr

    # 确定关系起始文件块号
    relation_start_blk_number = blk_dict[relation]
    present_blk_number = relation_start_blk_number
    data = []  # 保存满足条件的元组
    write_blk_index = buffer.getNewBlockInBuffer()  # 为选择的数据申请一个缓冲区
    if write_blk_index == -1:
        print("缓冲区已满！")
        return addr

    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满！")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 后继磁盘块号

        # 进行比对选择
        for i in range(int(number_of_tuple)):
            if int(read_data[i * 2 + attr_index]) == value:
                data.append([read_data[i * 2], read_data[i * 2 + 1]])
                print(relation, (read_data[i * 2], read_data[i * 2 + 1]))

        present_blk_number = next_blk_number  # 下一块
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        if present_blk_number == '0':
            break

    print(f'共找到{len(data)}条数据。')

    addr = write_data(data, int(ceil(len(data) / 7.0)), 7, addr)
    return addr


def project(relation, attribute, addr):
    if relation != 'R' and relation != 'S':
        print(f"关系{relation}不存在！")
        return addr

    if attribute == 'A' or attribute == 'C':
        attr_index = 0
    elif attribute == 'B' or attribute == 'D':
        attr_index = 1
    else:
        print(f"属性{attribute}不存在！")
        return addr

    # 确定关系的起始文件块号
    present_blk_number = blk_dict[relation]
    data = []  # 保存满足条件的元组
    write_blk_index = buffer.getNewBlockInBuffer()  # 为选择的数据申请一个缓冲区
    if write_blk_index == -1:
        print("缓冲区已满！")
        return addr

    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满！")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 继磁盘块号

        # 投影
        for i in range(int(number_of_tuple)):
            data.append([read_data[i * 2 + attr_index]])
            print(read_data[i * 2 + attr_index])

        present_blk_number = next_blk_number
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        if present_blk_number == '0':
            break

    print(f'共找到{len(data)}条数据。')
    addr = write_data(data, int(ceil(len(data) / 14.0)), 14, addr)
    return addr


def nest_loop_join(relation_first, relation_second, blk_numbers_of_first, blk_numbers_of_second,
                   blk_number):
    # 确定嵌套顺序，使开销最小
    if blk_numbers_of_first > blk_numbers_of_second:
        out_relation = relation_second
        in_relation = relation_first
    else:
        out_relation = relation_first
        in_relation = relation_second

    # 确定外层关系的起始文件块号
    out_present_blk_number = blk_dict[out_relation]
    data = []  # 匹配的元组
    write_blk_index = buffer.getNewBlockInBuffer()  # 为选择的数据申请一个缓冲区
    if write_blk_index == -1:
        print("缓冲区已满！")
        return blk_number

    while True:
        out_index = buffer.readBlockFromDisk(out_present_blk_number)  # 为关系的数据申请一个缓冲
        if out_index == -1:
            print("缓冲区已满！")
            break

        out_read_data = buffer.data[out_index][1]  # 读取的数据
        out_number_of_tuple = (len(out_read_data) - 1) / 2
        out_next_blk_number = out_read_data[-1]  # 后继磁盘块号

        # 确定内层关系的起始文件块号
        in_present_blk_number = blk_dict[in_relation]
        while True:
            in_index = buffer.readBlockFromDisk(in_present_blk_number)
            if in_index == -1:
                print("缓冲区已满！")
                exit()
            in_read_data = buffer.data[in_index][1]
            in_number_of_tuple = (len(in_read_data) - 1) / 2
            in_next_blk_number = in_read_data[-1]

            for i in range(int(out_number_of_tuple)):
                for j in range(int(in_number_of_tuple)):
                    if out_read_data[i * 2] == in_read_data[j * 2]:
                        data.append([int(out_read_data[i * 2]), int(out_read_data[i * 2 + 1]),
                                     int(in_read_data[j * 2 + 1])])
                        print(out_relation, (int(out_read_data[i * 2]), int(out_read_data[i * 2 + 1])), '-',
                              in_relation, (int(in_read_data[j * 2]), int(in_read_data[j * 2 + 1])))
            in_present_blk_number = in_next_blk_number
            buffer.freeBlockInBuffer(in_index)  # 释放内层关系缓冲区
            if in_present_blk_number == '0':
                break

        out_present_blk_number = out_next_blk_number
        buffer.freeBlockInBuffer(out_index)  # 释放外层关系缓冲区
        if out_present_blk_number == '0':
            break

    print(f'共连接{len(data)}条数据。')

    blk_number = write_data(data, int(ceil(len(data) / 5.0)), 5, blk_number)
    return blk_number


def hash_join(relation_first, relation_second, number_of_bucket, blk_number):
    if relation_first != 'R' and relation_first != 'S':
        print(f"关系{relation_first}不存在！")
        return blk_number
    elif relation_second != 'R' and relation_second != 'S':
        print(f"关系{relation_second}不存在！")
        return blk_number

    # 构造桶
    bucket_of_r = []
    bucket_of_s = []
    for i in range(number_of_bucket):
        bucket_of_r.append([])
        bucket_of_s.append([])

    # 确定第一个关系的起始文件块号
    present_blk_number = blk_dict[relation_first]
    # 读取第一个关系的数据
    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满！")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 后继磁盘块号

        # 读取所有的元组
        for i in range(int(number_of_tuple)):
            bucket_index = (int(read_data[i * 2]) + 2) % number_of_bucket  # hash
            bucket_of_r[bucket_index].append([int(read_data[i * 2]), int(read_data[i * 2 + 1])])
        present_blk_number = next_blk_number
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        # 读完退出
        if present_blk_number == '0':
            break

    # 第二个关系
    present_blk_number = blk_dict[relation_second]
    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满！")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 后继磁盘块号

        # 读取所有的元组
        for i in range(int(number_of_tuple)):
            bucket_index = (int(read_data[i * 2]) + 2) % number_of_bucket  # hash
            bucket_of_s[bucket_index].append([int(read_data[i * 2]), int(read_data[i * 2 + 1])])
        present_blk_number = next_blk_number
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        # 读完退出
        if present_blk_number == '0':
            break
    # join
    data = []
    for i in range(number_of_bucket):
        for j in range(len(bucket_of_r[i])):
            for k in range(len(bucket_of_s[i])):
                if bucket_of_r[i][j][0] == bucket_of_s[i][k][0]:
                    data.append(
                        [bucket_of_r[i][j][0], bucket_of_r[i][j][1], bucket_of_s[i][k][1]])
                    print(relation_first, tuple(bucket_of_r[i][j]),
                          '-', relation_second, tuple(bucket_of_s[i][k]))

    print(f'共连接{len(data)}条数据。')

    blk_number = write_data(data, int(ceil(len(data) / 5.0)), 5, blk_number)
    return blk_number


def sort_merge_join(relation_first, relation_second, blk_number):
    if relation_first != 'R' and relation_first != 'S':
        print(f"关系{relation_first}不存在！")
        return blk_number
    elif relation_second != 'R' and relation_second != 'S':
        print(f"关系{relation_second}不存在！")
        return blk_number

    first_data = []
    present_blk_number = blk_dict[relation_first]
    # 读取第一个关系的数据
    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满!")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 后继磁盘块号

        # 读取所有的元组
        for i in range(int(number_of_tuple)):
            first_data.append([int(read_data[i * 2]), int(read_data[i * 2 + 1])])
        present_blk_number = next_blk_number
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        # 读完退出
        if present_blk_number == '0':
            break

    second_data = []
    present_blk_number = blk_dict[relation_second]
    # 读取第二个关系的数据
    while True:
        index = buffer.readBlockFromDisk(present_blk_number)  # 为关系的数据申请一个缓冲
        if index == -1:
            print("缓冲区已满!")
            break

        read_data = buffer.data[index][1]  # 读取的数据
        number_of_tuple = (len(read_data) - 1) / 2
        next_blk_number = read_data[-1]  # 后继磁盘块号

        # 读取所有的元组
        for i in range(int(number_of_tuple)):
            second_data.append([int(read_data[i * 2]), int(read_data[i * 2 + 1])])
        present_blk_number = next_blk_number
        buffer.freeBlockInBuffer(index)  # 释放缓冲区
        # 读完退出
        if present_blk_number == '0':
            break
    # sort
    first_data = sorted(first_data, key=lambda t: t[0])
    second_data = sorted(second_data, key=lambda t: t[0])

    # merge
    data = []
    i = 0
    j = 0
    while i < len(first_data) or j < len(second_data):
        if i < len(first_data) and j < len(second_data):
            if first_data[i][0] == second_data[j][0]:
                data.append([first_data[i][0], first_data[i][1], second_data[j][1]])
                print(relation_first, first_data[i],
                      '-', relation_second, second_data[j])
                temp_index = j + 1  # 让第二个关系先移动
                while temp_index < len(second_data) and first_data[i][0] == \
                        second_data[temp_index][0]:
                    data.append(
                        [first_data[i][0], first_data[i][1], second_data[temp_index][1]])
                    print(relation_first, tuple(first_data[i]),
                          '-', relation_second, tuple(second_data[temp_index]))
                    temp_index += 1
                i += 1  # 只移动第二个关系不移动第一个关系
            elif first_data[i][0] < second_data[j][0]:
                i += 1
            elif first_data[i][0] > second_data[j][0]:
                j += 1
        else:
            break

    print(f'共连接{len(data)}条数据。')

    blk_number = write_data(data, int(ceil(len(data) / 5.0)), 5, blk_number)
    return blk_number


if __name__ == '__main__':
    blk_number = 0  # 磁盘块号
    blk_numbers_of_R = 16  # 关系R的磁盘块数
    blk_numbers_of_S = 32  # 关系S的磁盘块数
    blk_dict = {}  # 用于记录关系和关系存放的第一个文件块的编号

    buffer = extmem.Buffer(64, 8)

    r = []
    s = []
    generate_data(r, s)
    print('数据创建完成。')

    blk_dict['R'] = blk_number
    blk_number = write_relation(r, blk_numbers_of_R, blk_number)
    print(f'关系R写入至块号0至{blk_number-1}。')

    temp = blk_number

    blk_dict['S'] = blk_number
    blk_number = write_relation(s, blk_numbers_of_S, blk_number)
    print(f'关系R写入至块号{temp}至{blk_number-1}。')

    temp = blk_number

    print("选择操作结果：")
    blk_number = select('R', 'A', 40, blk_number)
    print(f"选择操作结果保存至块号{temp}至{blk_number-1}。")

    temp = blk_number

    print("投影操作结果：")
    blk_number = project('R', 'A', blk_number)
    print(f"投影操作结果保存至块号{temp}至{blk_number-1}。")

    temp = blk_number

    print("Nest-Loop-Join结果：")
    blk_number = nest_loop_join('R', 'S', blk_numbers_of_R, blk_numbers_of_S, blk_number)
    print(f"Nest-Loop Join操作结果保存至块号{temp}至{blk_number-1}。")

    temp = blk_number

    print("Hash_Join结果：")
    blk_number = hash_join('R', 'S', 5, blk_number)
    print(f"Hash Join操作结果保存至块号{temp}至{blk_number-1}。")

    temp = blk_number

    print("Sort_Merge_Join结果：")
    blk_number = sort_merge_join('R', 'S', blk_number)
    print(f"Sort-Merge Join操作结果保存至块号{temp}至{blk_number-1}。")
