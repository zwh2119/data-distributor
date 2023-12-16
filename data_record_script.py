import json
import os

total_cnt = 0
error_cnt = 0

for file in os.listdir('data_record'):

    path = os.path.join('data_record', file)
    total_cnt += 1
    with open(path, 'r') as f:
        data = json.load(f)
        for service in data['pipeline']:
            if service['execute_data']['transmit_time']<0:
                # print('Error')
                print(file)
                print(data)
                print()
                error_cnt += 1

print('total_cnt:', total_cnt)
print('error_cnt:', error_cnt)
