# include <stdio.h>
# include <string.h>
# include <stdlib.h>

# define TABLE_SIZE 786307 // From the previous exercise

int hash_function(char *word, int table_size) {
  int hash = 4291;
  for (int i = 0; i < strlen(word); i++) {
    hash ^= ((hash << 5) + (hash >> 2) + word[i]) % table_size;
  }
  return hash % table_size;
}

// Search for a word in the hash table using open addressing
int open_addressing_search(char *table[], char *word, int table_size) {
  int hash = hash_function(word, table_size);
  int initial_hash = hash;

  // Linear probing
  while (table[hash] != NULL) {
    // Check if the word is found
    if (strcmp(table[hash], word) == 0) {
      return 1; // Word found
    }
    hash = (hash + 1) % table_size;

    // Check if we have looped around to the starting point
    if (hash == initial_hash) {
      break; // Word not found, break the loop
    }
  }
  return 0; // Word not found
}

// Insert a word into the hash table using open addressing
void open_addressing_insert(char *table[], char *word, int table_size) {
  int hash = hash_function(word, table_size);
  // Linear probing
  while (table[hash] != NULL) {
    if (strcmp(table[hash], word) == 0) {
      return; // Word already exists, no need to insert again
    }
    hash = (hash + 1) % table_size;
  }
  table[hash] = strdup(word);
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    printf("Usage: %s file1 file2\n", argv[0]);
    exit(1);
  }

  FILE *file1 = fopen(argv[1], "r");
  if (file1 == NULL) {
    fprintf(stderr, "Error: Cannot open file %s\n", argv[1]);
    exit(1);
  }

  FILE *file2 = fopen(argv[2], "r");
  if (file2 == NULL) {
    fprintf(stderr, "Error: Cannot open file %s\n", argv[2]);
    fclose(file1);
    exit(1);
  }

  // Open addressing ------------------------------------------------------------------------------
  printf("Open addressing:\n");
  // Data structure for open addressing hash table
  char *open_addressing_table[TABLE_SIZE] = {0}; // Initialize all entries to NULL

  // Insert words from file1 into the hash table
  // Use open addressing to handle collisions
  char word[100];
  while (fscanf(file1, "%s", word) != EOF) {
    open_addressing_insert(open_addressing_table, word, TABLE_SIZE);
  }

  // Search for intersections
  int nb_intersections = 0;
  char *intersections[TABLE_SIZE] = {0};
  while (fscanf(file2, "%s", word) != EOF) {
    if (open_addressing_search(open_addressing_table, word, TABLE_SIZE)) {
      printf("%s\n", word);
      nb_intersections++;
    }
  }
  printf("Total intersections: %d\n", nb_intersections);
  // ----------------------------------------------------------------------------------------------
  
  // Close files
  fclose(file1);
  fclose(file2);

  // Free memory allocated for hash table entries
  for (int i = 0; i < TABLE_SIZE; i++) {
    free(open_addressing_table[i]);
  }

  return 0;
}
