import socket

head = [0x0d,0x05]
enctry = [0x00]
ver = [0x19]
source_id = [0x12,0x4e,0x25,0xf3,0xa4,0x3c,0x44,0x82,0xbc,0x95,0x80,0x68,0xc7,0x59,0x3c,0x85]
tail = [0x0d,0x0a]
raw_data_len = [0x00,0x00]
head_len = [0x00,0x00]
AVN = [0x4e,0x33,0x33,0x31,0x30,0x31,0x30,0x31,0x30,0x33,0x30,0x30,0x30,0x32,0x31,0x34]
LEN_POS = 1


class data:
    len = [0x00,0x00]

    def __init__(self,request_num,len,data_type,profession_data):
        self.request_num = request_num
        self.len[1] = len
        self.data_type = data_type
        self.profession_data = profession_data
        self.body = []

    def __get_body(self):
        body = self.request_num
        if(self.len!=0):
            body = body+self.len+self.data_type+self.profession_data
        return body

    def __check_sum(self,data):
        checksum = 0
        for i in data:
            checksum += i
            checksum &= 0xFF
        return checksum        
        
    def get_data(self):
        data = enctry+ver+source_id+self.__get_body()
        msg_len = len(data)+1
        data.insert(0,0)
        data.insert(1,msg_len)
        sum = self.__check_sum(data)
        data = data+[sum]
        data = head+data+tail
        return data

    def dbg(self):
        data = self.get_data()
        for tmp in data:
            print(hex(tmp))

if __name__ == '__main__' :
    data = data([0x05,0x04],2,[0x01],[0x00])
    host_data = data.get_data()
    data.dbg()
