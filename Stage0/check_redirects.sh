#!/bin/bash
# 重定向检查脚本
# 用法: cat paths.txt | ./check_redirects.sh > redirects.csv

BASE_URL="https://www.omniglot.com"
MAX_JOBS=20

check_redirect() {
    local path="$1"
    local url="${BASE_URL}${path}"
    
    local response curl_exit_code
    response=$(curl -s -I -L -w "%{url_effective}|%{http_code}" --connect-timeout 10 --max-time 30 --retry 3 "$url" 2>/dev/null)
    curl_exit_code=$?
    
    if [ $curl_exit_code -eq 0 ] && [[ "$response" == *"|"* ]]; then
        local final_url status_code final_path is_redirect is_available
        final_url=$(echo "$response" | tail -1 | cut -d'|' -f1)
        status_code=$(echo "$response" | tail -1 | cut -d'|' -f2)
        final_path="${final_url#$BASE_URL}"
        
        if [[ ! "$status_code" =~ ^[0-9]+$ ]]; then
            status_code="0"
        fi
        
        if [ "$path" != "$final_path" ]; then
            is_redirect="true"
        else
            is_redirect="false"
        fi
        
        if [ "$status_code" = "200" ]; then
            is_available="true"
        else
            is_available="false"
        fi
        
        echo "$path,$final_path,$status_code,$is_redirect,$is_available"
    else
        echo "$path,$path,CURL_ERROR,false,false"
    fi
}

export -f check_redirect
export BASE_URL

# 写CSV头
echo "source_path,target_path,status_code,is_redirect,is_available"

# 并行检查
xargs -I {} -P $MAX_JOBS bash -c 'check_redirect "$@"' _ {}
