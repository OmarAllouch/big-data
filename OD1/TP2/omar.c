# include <stdio.h>
# include <string.h>
# include <stdlib.h>

# define TABLE_SIZE 786307 // From the previous exercise

typedef struct {
  char *word;
  int hash;
} Word;

typedef struct {
  Word *words;
  int size;
} Table;

FILE *open_file(char *file_name, char *mode) {
  FILE *file = fopen(file_name, mode);
  if (file == NULL) {
    printf("Error: Could not open file %s\n", file_name);
    exit(1);
  }
  return file;
}

int hash_function(char *word, int table_size) {
  int hash = 4291;
  for (int i = 0; i < strlen(word); i++) {
    hash ^= (hash << 5) + (hash >> 2) + word[i];
  }
  return hash % table_size;
}

int main(int argc, char *argv[]) {
  FILE *file1 = open_file(argv[1], "r");
  FILE *file2 = open_file(argv[2], "r");

  Table table[TABLE_SIZE];

  char word[100];
  int collisions = 0;
  while (fscanf(file1, "%s", word) != EOF) {
    int hash = hash_function(word, TABLE_SIZE);
    if (table[hash].size == 0) {
      table[hash].words = malloc(sizeof(Word));
      table[hash].words[0].word = strdup(word);
      table[hash].words[0].hash = hash;
      table[hash].size++;
    } else {
      int i = 0;
      while (i < table[hash].size && strcmp(table[hash].words[i].word, word) != 0) {
        i++;
      }
      if (i == table[hash].size) {
        table[hash].words = realloc(table[hash].words, (table[hash].size + 1) * sizeof(Word));
        table[hash].words[table[hash].size].word = strdup(word);
        table[hash].words[table[hash].size].hash = hash;
        table[hash].size++;
      } else {
        collisions++;
      }
    }
  }
  printf("# collisions: %d\n", collisions);

  int nb_intersections = 0;
  while (fscanf(file2, "%s", word) != EOF) {
    int hash = hash_function(word, TABLE_SIZE);
    for (int i = 0; i < table[hash].size; i++) {
      if (strcmp(table[hash].words[i].word, word) == 0) {
        nb_intersections++;
        break;
      }
    }
  }
  printf("# intersections: %d\n", nb_intersections);

  return 0;
}
