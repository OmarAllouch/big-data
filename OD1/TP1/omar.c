# include <stdio.h>
# include <string.h>
# include <math.h>
# include <stdlib.h>

# define MAX_OCCUPANCY_RATE 0.30
# define INITIAL_SIZE 235885 // Number of lines = number of distinct words in word.txt
// 22906, 58110

int is_prime(int n) {
  if (n <= 1) {
    return 0;
  }
  for (int i = 2; i <= sqrt(n); i++) {
    if (n % i == 0) {
      return 0;
    }
  }
  return 1;
}

int next_prime(int n) {
  while (!is_prime(n)) {
    n++;
  }
  return n;
}

int calculate_table_size(int distinct_words) {
  int table_size = (int)(distinct_words / MAX_OCCUPANCY_RATE);
  return next_prime(table_size);
}

int hash_function(char *word, int table_size) {
  int hash = 4291;
  for (int i = 0; i < strlen(word); i++) {
    hash ^= (hash << 5) + (hash >> 2) + word[i];
  }
  return hash % table_size;
}

int other_hash_function(char *word, int table_size) {
  int hash = 33;
  for (int i = 0; i < strlen(word); i++) {
    hash += word[i];
    hash *= (hash << 4);
    hash ^= (hash >> 10);
  }
  return hash % table_size;
}

int main(int argc, char *argv[]) {
  FILE *file = fopen("corncob lowercase.txt", "r");

  if (file == NULL) {
    printf("Error: Could not open file\n");
    return 1;
  }

  int table_size = calculate_table_size(INITIAL_SIZE);
  printf("Table size: %d\n", table_size);

  __uint8_t table[table_size];
  for (int i = 0; i < table_size; i++) {
    table[i] = 0;
  }

  int collisions = 0;
  char word[100];
  while (fgets(word, sizeof(word), file)) {
    int hash = hash_function(word, table_size);
    if (table[hash] != 0) {
      collisions++;
    } else {
      table[hash] = 1;
    }
  }
  printf("Collisions: %d\n", collisions);

  fclose(file);
  return 0;
}
