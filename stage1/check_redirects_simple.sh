#!/bin/bash
# 简单的Omniglot重定向检查脚本
# 用法: ./check_redirects_simple.sh < absolute_path_list.txt

BASE_URL="https://www.omniglot.com"

while read -r path; do
    # 跳过空行和注释
    [[ -z "$path" || "$path" =~ ^# ]] && continue
    
    # 移除Fragment部分用于HTTP请求
    clean_path="${path%#*}"
    full_url="${BASE_URL}${clean_path}"
    
    # 获取响应头，跟踪重定向
    response=$(curl -s -I -L --max-redirs 5 --connect-timeout 10 "$full_url" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        status=$(echo "$response" | grep "^HTTP" | tail -1 | awk '{print $2}')
        redirect_count=$(echo "$response" | grep -c "^HTTP")
        
        if [ "$redirect_count" -gt 1 ]; then
            final_url=$(curl -s -I -L --max-redirs 5 -w "%{url_effective}" "$full_url" 2>/dev/null | tail -1)
            final_path="${final_url#$BASE_URL}"
            echo "$path -> $final_path ($status)"
        else
            echo "$path: $status"
        fi
    else
        echo "$path: ERROR"
    fi
    
    sleep 1
done
