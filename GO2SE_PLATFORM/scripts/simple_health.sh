#!/bin/bash
# 最简健康检查 - 只ping后端，不做任何复杂操作
curl -s --max-time 5 http://localhost:8004/api/ping && echo " OK" || echo " FAIL"
