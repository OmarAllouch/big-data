# include <stdio.h>
# include <string.h>
# include <stdlib.h>

# define TABLE_SIZE 786307 // From the previous exercise

typedef struct Node {
  char *word;
  struct Node *next;
} Node;

typedef struct HashTable {
  Node *words[TABLE_SIZE];
} HashTable;

int hash_function(char *word, int table_size) {
  int hash = 4291;
  for (int i = 0; i < strlen(word); i++) {
    hash ^= ((hash << 5) + (hash >> 2) + word[i]) % table_size;
  }
  return hash % table_size;
}

// Search for a word in the hash table using chaining
int chaining_search(HashTable *table, char *word, int table_size) {
  int hash = hash_function(word, table_size);
  Node *current = table->words[hash];
  while (current != NULL) {
    if (strcmp(current->word, word) == 0) {
      return 1; // Word found
    }
    current = current->next;
  }
  return 0; // Word not found
}

// Insert a word into the hash table using chaining
void chaining_insert(HashTable *table, char *word, int table_size) {
  int hash = hash_function(word, table_size);
  Node *new_node = malloc(sizeof(Node));
  new_node->word = strdup(word);
  new_node->next = NULL;
  if (table->words[hash] == NULL) {
    table->words[hash] = new_node; 
  } else {
    new_node->next = table->words[hash];
    table->words[hash] = new_node;
  }
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

  // Chaining -------------------------------------------------------------------------------------
  printf("Chaining:\n");
  // Data structure for chaining hash table
  HashTable chaining_table;
  for (int i = 0; i < TABLE_SIZE; i++) {
    chaining_table.words[i] = NULL;
  }

  // Insert words from file1 into the hash table
  // Use chaining to handle collisions
  char word[100];
  while (fscanf(file1, "%s", word) != EOF) {
    chaining_insert(&chaining_table, word, TABLE_SIZE);
  }

  // Search for intersections
  int nb_intersections = 0;
  char *intersections[TABLE_SIZE] = {0};
  while (fscanf(file2, "%s", word) != EOF) {
    if (chaining_search(&chaining_table, word, TABLE_SIZE)) {
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
    Node *current = chaining_table.words[i];
    while (current != NULL) {
      Node *temp = current;
      current = current->next;
      free(temp->word);
      free(temp);
    }
  }

  return 0;
}
