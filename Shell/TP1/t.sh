for d in $(
	sed -n '2p;$p' 20200423-062902-metrics-daily.csv |
		cut -d , -f 2 |
		awk '{ printf "%d\n",$0/100000000 }'
); do
	date -d@"$d"
done
