import exemple_f_hash as f_hash
import sys


def bloom_filter_intersection(file1, file2, size, num_hash):
    # Open files
    f1 = open(file1, "r")
    f2 = open(file2, "r")

    # Create bloom filter
    bloom_filter = [0] * size

    # Hash functions
    functions = [
        f_hash.le1_bon_hashage,
        f_hash.le2_bon_hachage,
        f_hash.le2_hachage_original,
        f_hash.co1_hachage_original,
        f_hash.co1_bon_hachage,
        f_hash.al_hachage,
        f_hash.el1_bon_hachage,
        f_hash.el_autre_hachage,
    ]

    # Insert words from file1 into bloom filter
    for line in f1:  # Single word per line
        word = line.strip()
        for k in range(num_hash):
            index = functions[k](word, size)
            bloom_filter[index] = 1

    # Count words from file2 that are in file1
    count = 0
    for line in f2:  # Single word per line
        is_in = True
        word = line.strip()
        for k in range(num_hash):
            index = functions[k](word, size)
            if (
                bloom_filter[index] == 0
            ):  # If one hash function returns 0, the word is not in file1
                is_in = False
                break
        if is_in:
            count += 1

    # Close files
    f1.close()
    f2.close()

    return count


def benchmark():
    # Files
    file1 = "texte Shakespeare.txt"
    file2 = "corncob lowercase.txt"

    # Sizes and number of hash functions
    sizes = [1000, 10000, 100000, 1000000]
    num_hashes = [1, 2, 3, 4, 5, 6, 7, 8]

    # Benchmark
    for size in sizes:
        for num_hash in num_hashes:
            print("Size: " + str(size) + ", Num hash: " + str(num_hash))
            print(bloom_filter_intersection(file1, file2, size, num_hash))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 main.py file1 file2 size num_hash")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    size = int(sys.argv[3])
    num_hash = int(sys.argv[4])

    # benchmark()
    print(
        "Potential number of intersections:",
        bloom_filter_intersection(file1, file2, size, num_hash),
    )
