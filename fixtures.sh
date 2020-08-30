#!/bin/bash

set -e
set -o pipefail

webcheckctl websites create --hostname aiven.com
webcheckctl checks create --website-id 1 --interval 30
webcheckctl checks create --website-id 1 --interval 30 --expect-http-code 400
