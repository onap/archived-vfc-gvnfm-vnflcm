# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

env_dict = os.environ

# [MSB]
MSB_BASE_URL = env_dict.get("MSB_HOST", "http://127.0.0.1:80")
MSB_ENABLED = env_dict.get("MSB_ENABLED", True)

# [mysql]
DB_IP = env_dict.get("MYSQL_ADDR", "127.0.0.1:3306").split(':')[0]
DB_PORT = env_dict.get("MYSQL_ADDR", "127.0.0.1:3306").split(':')[1]
DB_NAME = "gvnfm"
DB_USER = "gvnfm"
DB_PASSWD = "gvnfm"

# [REDIS]
REDIS_HOST = env_dict.get("REDIS_HOST", DB_IP)
REDIS_PORT = '6379'
REDIS_PASSWD = ''

# [MDC]
SERVICE_NAME = "vnflcm"
FORWARDED_FOR_FIELDS = ["HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_HOST",
                        "HTTP_X_FORWARDED_SERVER"]

# [aai config]
AAI_BASE_URL = "http://127.0.0.1:80/aai/v13"
AAI_USER = "AAI"
AAI_PASSWD = "AAI"

# [register]
REG_TO_MSB_WHEN_START = env_dict.get("REG_TO_MSB_WHEN_START", "false")
SSL_ENABLED = env_dict.get("SSL_ENABLED", "false")
REG_TO_MSB_REG_URL = "/api/microservices/v1/services"
REG_TO_MSB_REG_PARAM = {
    "serviceName": "vnflcm",
    "version": "v1",
    "enable_ssl": SSL_ENABLED,
    "url": "/api/vnflcm/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": "127.0.0.1",
        "port": "8801",
        "ttl": 0
    }]
}
MSB_SVC_URL = "/api/microservices/v1/services/vnflcm/version/v1"
