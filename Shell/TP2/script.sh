#!/bin/bash

# Function to print usage information
print_usage() {
	echo "Usage: $0 [OPTIONS...] LOG_FILE"
	echo "Options:"
	echo "  -u: Get successful users"
	echo "  -U: Get rejected users"
	echo "  -i: Get successful IPs"
	echo "  -I: Get rejected IPs"
	echo "  -b: Get blocked IPs"
	echo "  -B: Get blocked IPs with duration"
	echo "  -n: Get unsuccessful blocked IPs"
	echo "  -d: Calculate average blocked time"
	echo "  -D IP: Get IP attack start and end dates"
	echo "  -f: Calculate average weekly frequency of successful connections"
	echo "  -F: Calculate average daily frequency of unsuccessful connections"
	echo "  -c: Get successful connections in CSV format"
	echo "  -C: Get unsuccessful connections in CSV format"
}

# Check if the first argument is a file
if [[ -f "$1" ]]; then
	log_file=$1
	option=$2
	if [[ $option == "-D" ]]; then
		if [[ -f "$3" ]]; then
			echo "Please provide an IP address"
			exit 1
		else
			ip=$3
		fi
	fi
else
	option=$1
	if [[ $option == "-D" ]]; then
		if [[ -f "$2" ]]; then
			echo "Please provide an IP address"
			exit 1
		else
			ip=$2
			log_file=$3
		fi
	else
		log_file=$2
	fi
fi

# Function to extract successful users' IDs
get_successful_users() {
	awk '/Accepted/ {print $9}' "$log_file" | sort | uniq -c |
		# Puts the count after the user ID
		awk '{print $2, $1}'
}

# Function to extract rejected users' IDs
get_rejected_users() {
	awk '/: Invalid user [[:alnum:]_]+ from/ {print $8}' "$log_file" | sort | uniq -c |
		# Puts the count after the user ID
		awk '{print $2, $1}'
}

# Function to extract successful users' IPs
get_successful_ips() {
	awk '/Accepted/ {print $11}' "$log_file" | sort | uniq
}

# Function to extract rejected users' IPs
get_rejected_ips() {
	awk '/: Invalid user [[:alnum:]_]+ from/ {print $10}' "$log_file" | sort | uniq
}

# Function to extract blocked IPs
get_blocked_ips() {
	# Get the IPs that were blocked
	awk '/: Blocking/ {print $7, $9}' "$log_file" | sort | uniq -c |
		# Puts the count after the IP
		awk '{print $2, $1}'
}

# Function to extract blocked IPs and their durations
get_blocked_ips_with_duration() {
	# Get the IPs that were blocked and their durations
	awk '/: Blocking/ {print $7, $9}' "$log_file" | sort | uniq |
		# Calculate the total duration for each IP
		awk '{sum[$1]+=$2} END {for (ip in sum) print ip, sum[ip], "secs"}'
}

# Function to extract unsuccessful IPs that were not blocked
get_unsuccessful_blocked_ips() {
	# Gets the IPs that were rejected
	awk '/: Invalid user [[:alnum:]_]+ from/ {print $10}' "$log_file" | sort | uniq |
		# Removes the IPs that were blocked
		awk '!/Blocking/'
}

# Function to calculate average duration of blocked IPs
calculate_average_blocked_time() {
	# Gets the blocked IPs and their durations
	awk '/: Blocking/ {print $7, $9}' "$log_file" | sort | uniq |
		# Calculates the total duration for each IP
		awk '{sum[$1]+=$2; count[$1]++} END {for (ip in sum) print sum[ip]}' |
		# Calculates the average
		awk '{sum += $1; n++} END {if (n > 0) print sum / n; else print 0}'
}

# Function to extract IP attacks and their dates
get_ip_attack_dates() {
	# Compare the IP address with the one provided
	awk -v ip="$1" '$8 == "\"" ip "\"" {print $1, $2, $3}' "$log_file" |
		# Sort by date
		sort -k1M -k2n -k3 |
		# Print first and last date
		awk 'NR == 1 {print} END {print}'
}

# Function to calculate average weekly frequency of successful connections
calculate_average_weekly_frequency() {
	# Extract successful connections
	awk '/Accepted/ {print $1, $2}' "$log_file" |
		# Extract the month and day
		while read -r month day; do date -d "$month $day" +%Y-%U; done |
		# Count the number of unique weeks
		uniq -c |
		# Calculate the average
		awk '{total += $1} END {print total / NR}'
}

# Function to calculate average daily frequency of unsuccessful connections
calculate_average_daily_frequency() {
	# Extract unsuccessful connections
	awk '/: Invalid user [[:alnum:]_]+ from/ {print $1, $2}' "$log_file" | uniq -c |
		# Calculate the average
		awk '{sum += $1; n++} END {if (n > 0) print sum / n; else print 0}'
}

# Function to extract successful connections in CSV format
get_successful_connections_csv() {
	echo "Date,Timestamp,Server,IP,User"
	# First 3 fields should be converted to timestamp
	awk '/Accepted/ {print $1, $2, $3, $4, $9, $11}' "$log_file" |
		while read -r month day time server user ip; do
			# Convert date and time to timestamp
			date=$(date -d "$month $day" +%Y-%m-%d)
			# Use date and time time to get timestamp
			ts=$(date -d "$date $time" +%s)
			echo "$date,$ts,$server,$ip,$user"
		done
}

# Function to extract unsuccessful connections in CSV format
get_unsuccessful_connections_csv() {
	echo "Date,Timestamp,Server,IP,User"
	# First 3 fields should be converted to timestamp
	awk '/: Invalid user [[:alnum:]_]+ from/ {print $1, $2, $3, $4, $8, $10}' "$log_file" |
		while read -r month day time server user ip; do
			# Convert date and time to timestamp
			date=$(date -d "$month $day" +%Y-%m-%d)
			# Use date and time time to get timestamp
			ts=$(date -d "$date $time" +%s)
			echo "$date,$ts,$server,$ip,$user"
		done
}

# Function to verify IP address
validate_ip() {
	# Check if the IP address is valid
	if [[ ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
		echo "Invalid IP address: $1"
		exit 1
	fi
}

# Main script logic
if [[ -z "$log_file" || -z "$option" ]]; then
	print_usage
	exit 1
fi

case "$option" in
-u)
	get_successful_users
	;;
-U)
	get_rejected_users
	;;
-i)
	get_successful_ips
	;;
-I)
	get_rejected_ips
	;;
-b)
	get_blocked_ips
	;;
-B)
	get_blocked_ips_with_duration
	;;
-n)
	get_unsuccessful_blocked_ips
	;;
-d)
	calculate_average_blocked_time
	;;
-D)
	validate_ip "$ip"
	get_ip_attack_dates "$ip"
	;;
-f)
	calculate_average_weekly_frequency
	;;
-F)
	calculate_average_daily_frequency
	;;
-c)
	get_successful_connections_csv
	;;
-C)
	get_unsuccessful_connections_csv
	;;
*)
	echo "Invalid option: $option"
	print_usage
	exit 1
	;;
esac
