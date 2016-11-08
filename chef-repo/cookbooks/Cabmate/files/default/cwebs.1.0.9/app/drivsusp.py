import struct

file_name = "/data/drivsusp.fl"
'''
record  3 (1054, 23, 1437755594, 11450, '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 'test mkravets\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', '1', '2', 1054, 1, 'X', 'XXXXXXX\x00\x00')
'''

'''
    driver_id As Long
    susp_duration As Long
    susptime As Long
    oper_id As Integer
    reason1 As String * 33
    reason2 As String * 33
    comp_num As Byte
    spare As Byte
    taxi As Integer
    fleet As Integer
    LimitReinstate As String * 1
    junk As String * 9 
'''
print 'opening file ', file_name
frmt = 'I I I h 33s 33s c c h h 10s'

try:
    counter = 0 
    fp = open(file_name, "r")
    while True:
        counter = counter + 1 
        data = fp.read(96)
        if data:
            print counter 
            tmp = struct.unpack(frmt, data)
            print tmp
        else:
            print counter, 'data is None'
            break
    fp.close()
except Exception as e:
    print 'exception ', str(e)
s = struct.Struct('I I I h 33s 33s c c h h 10s')
print s.size
#tmp = struct.unpack(frmt, data)

