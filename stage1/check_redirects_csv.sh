#!/bin/bash
# 简单的重定向检查脚本，输出CSV格式
# 用法: ./check_redirects_csv.sh < path_list.txt > redirects.csv

BASE_URL="https://www.omniglot.com"

echo "source_path,target_path,status_code"

while read -r path; do
    [[ -z "$path" || "$path" =~ ^# ]] && continue
    
    clean_path="${path%#*}"
    full_url="${BASE_URL}${clean_path}"
    
    response=$(curl -s -I -L --max-redirs 5 --connect-timeout 10 -w "%{http_code}|%{url_effective}" "$full_url" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        status=$(echo "$response" | tail -1 | cut -d'|' -f1)
        final_url=$(echo "$response" | tail -1 | cut -d'|' -f2)
        final_path="${final_url#$BASE_URL}"
        echo "$clean_path,$final_path,$status"
    else
        echo "$clean_path,,"
    fi
    
    sleep 1
done
