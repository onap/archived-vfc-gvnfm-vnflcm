Copyright 2017 ZTE Corporation.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Micro service of vnf life cycle management.

1. Code structure guide
   ./         vnflcm project files
   ./docker   vnflcm docker related scripts
   ./logs     vnflcm log file
   ./lcm      vnf life cycle management
       ./nf      vnf life cycle API& logic
             ./               API url and const
             ./views          API related VNF views, each operation is a view
             ./serializers    API related request and response parametes.
                              Suggest related to sol003, each datatype is a file.
                              Common datatypes are put into the common file
             ./biz            VNF LCM mangement busyness logic files
             ./tests          all the test case. At least each API should have a test case
       ./jobs      vnf lcm related job
       ./pub       common class, including database, external micro service API, utils, and config parameters.
       ./samples   vnflcm micro service health check
       ./swagger   auto-generate vnflcm swagger
