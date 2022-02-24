# kubecis
- 1.1.9, 1.1.10 執行 <br> 
    ```bash
    "find /var/lib/cni/networks -type f 2> /dev/null | xargs --no-run-if-empty stat -c %U:%G" 
    ```
    會因權限不足而無法進行驗證