#include "general.h"
#include "patricia_trie.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void nettoyage(char *ligne, char *mot_propre) {
  int i = 0, j = 0;

  while (ligne[i] != '\0') {
    if ((ligne[i] >= DEBUT) && (ligne[i] <= DEBUT + NALPHABET)) {
      mot_propre[j] = ligne[i];
      j++;
    }
    i++;
  }

  mot_propre[j] = '\0';
}

int main() {
  ABR mon_Patricia;
  FILE *fichier1, *fichier2;
  char f1[50], f2[50];
  char ligne[TAILLE_MAX], mot[TAILLE_MAX];

  // Fichier 1
  printf("Fichier 1 : ");
  scanf("%s", f1);

  // Fichier 2
  printf("Fichier 2 : ");
  scanf("%s", f2);

  fichier1 = fopen(f1, "r");
  if (fichier1 == NULL) {
    printf("erreur ouverture fichier %s.\n", f1);
    exit(2);
  }

  cree_racine_Patricia(&mon_Patricia);
  while (!feof(fichier1) && (fgets(ligne, sizeof ligne, fichier1) != NULL)) {
    nettoyage(ligne, mot);
    if (strlen(mot) != 0)
      insert_Patricia(mon_Patricia, mot);
  }
  fclose(fichier1);

  /* a mettre en commentaire pour des grands fichiers */
  // affiche_Patricia(mon_Patricia);

  fichier2 = fopen(f2, "r");
  if (fichier2 == NULL) {
    printf("erreur ouverture fichier %s.\n", f2);
    exit(2);
  }

  int count = 0;
  while (!feof(fichier2) && (fgets(ligne, sizeof ligne, fichier2) != NULL)) {
    nettoyage(ligne, mot);
    if (strlen(mot) != 0)
      if (recherche_Patricia(mon_Patricia, mot))
        count++;
  }
  fclose(fichier2);

  printf("Nombre de mots communs : %d\n", count);
  return 0;
}

