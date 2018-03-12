
def main(filename):
    filein = open(filename, 'r')
    fileout = open(filename+'.csv', 'w+')

    fileout.write('uid,type,value,timestamp,extra\n')

    i = 0
    for line in filein:
        i += 1
        if line and line != '\n':
            item_list = line.split(';')
            for item in item_list:
                if item and item != '\n':
                    item_dict = dict()
                    kv_list = item.split(',')
                    for kv in kv_list:
                        k = kv.split(':')[0]
                        v = kv.split(':')[1]
                        item_dict[k] = v
                    output = item_dict['uid'] + ',' + item_dict['type'] + \
                     ',' + item_dict['value'] + ',' + item_dict['timestamp'] + ','
                    first_flag = True
                    for key in sorted(item_dict):
                        if key not in ['uid', 'type', 'value', 'timestamp']:
                            if first_flag:
                                output += (key + ':' + item_dict[key])
                                first_flag = False
                            else:
                                output += ('|' + key + ':' + item_dict[key])
                    if output:
                        fileout.write(output)
                        fileout.write('\n')

    filein.close()
    fileout.close()


if __name__ == '__main__':
    filename = 'raw_data'
    main(filename)
