#!/bin/bash
echo "----------------"
echo "HMDT"
sed -n '2,$p' 20200423-062902-metrics-daily.csv | cat | awk -F, '$2!="" {print $6}' | sort | uniq
echo "----------------"
echo "LUMI"
sed -n '2,$p' 20200423-062902-metrics-daily.csv | cat | awk -F, '$3!="" {print $6}' | sort | uniq
echo "----------------"
