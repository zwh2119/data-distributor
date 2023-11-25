from fastapi import FastAPI, BackgroundTasks

from fastapi.routing import APIRoute
from starlette.responses import JSONResponse
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

import numpy as np
import os
import json

from utils import record_time

# TODO: deprecate this method in a later version
from set_environment import set_environment


# set_environment()


class DistributorServer:
    def __init__(self):
        self.app = FastAPI(routes=[
            APIRoute('/distribute',
                     self.deal_response,
                     response_class=JSONResponse,
                     methods=['POST']

                     ),
        ], log_level='trace', timeout=6000)

        self.app.add_middleware(
            CORSMiddleware, allow_origins=["*"], allow_credentials=True,
            allow_methods=["*"], allow_headers=["*"],
        )

    # TODO: check if the editing of file will conflict (multi-process in gunicorn)
    def record_process_data(self, source_id, task_id, content_data):
        file_path = f'data_record_source_{source_id}.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}

        data[task_id] = content_data

        with open(file_path, 'w') as f:
            json.dump(data, f)

    def distribute_data(self, data):
        pipeline = data['pipeline_flow']
        tmp_data = data['tmp_data']
        index = data['cur_flow_index']
        content = data['content_data']
        scenario = data['scenario_data']

        # end record transmit time
        tmp_data, transmit_time = record_time(tmp_data, f'transmit_time_{index}')
        assert transmit_time != -1
        pipeline[index]['execute_data']['transmit_time'] = transmit_time

        num = np.mean(scenario['obj_num'])
        size = np.mean(scenario['obj_size'])
        source_id = data['source_id']
        task_id = data['task_id']
        print(f'source:{source_id}, task:{task_id}, average car: {num}')

        record_data = {'obj_num': num, 'obj_size': size, 'pipeline': pipeline}
        self.record_process_data(source_id, task_id, record_data)

        # TODO: post data to aggregator

    async def deal_response(self, request: Request, backtask: BackgroundTasks):
        data = await request.json()
        backtask.add_task(self.distribute_data, data)
        return {'msg': 'data send success!'}


server = DistributorServer()
app = server.app
