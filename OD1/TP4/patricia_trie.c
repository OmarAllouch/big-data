#include "patricia_trie.h"
#include "general.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void cree_racine_Patricia(ABR *racine) {
  int i;
  *racine = (ABR)malloc(sizeof(struct noeud));
  for (i = 0; i < NALPHABET; i++) {
    (*racine)->cle[i] = NULL;
    (*racine)->fin[i] = 0;
    (*racine)->fils[i] = NULL;
  }
}

void affiche_Patricia(ABR racine) {
  // printf("== debut affichage ==\n");
  char mot_courant[TAILLE_MAX];
  int est_fin;

  mot_courant[0] = '\0';
  est_fin = FALSE;
  affiche_rec(racine, mot_courant, est_fin);
  // printf(" --- fin affichage --- \n");
}

void affiche_rec(ABR racine, char *partie_haute, int est_fin) {
  int i;
  char mot_courant[TAILLE_MAX];
  char temp[TAILLE_MAX];

  if (est_fin == TRUE)
    printf(" %s\n", partie_haute);
  if (racine == NULL)
    return;
  for (i = 0; i < NALPHABET; i++) {
    if (racine->cle[i] != NULL) {
      strcpy(temp, partie_haute);
      strcpy(mot_courant, strcat(temp, racine->cle[i]));
      affiche_rec(racine->fils[i], mot_courant, racine->fin[i]);
    }
  }
  return;
}

void insert_Patricia(ABR racine, char *valeur) {
  int i, j, indice;
  int position, pos_bis;
  ABR branche;
  char temp[TAILLE_MAX], reste[TAILLE_MAX], commun[TAILLE_MAX];

  position = valeur[0] - DEBUT;

  if (racine->cle[position] == NULL) {
    racine->cle[position] = malloc(TAILLE_MAX * sizeof(char));
    strcpy(racine->cle[position], valeur);
    racine->fin[position] = TRUE;
    return;
  } else {
    if (strcmp(racine->cle[position], valeur) == 0) {
      racine->fin[position] = TRUE;
      return;
    }

    indice = 0;
    while (racine->cle[position][indice] == valeur[indice])
      indice++;

    if (racine->cle[position][indice] == '\0') {
      // la valeur dépasse la chaine gardée
      j = indice;
      while (valeur[j] != '\0') {
        temp[j - indice] = valeur[j];
        j++;
      }
      temp[j - indice] = '\0';

      // insertion du morceaux qui dépasse
      if (racine->fils[position] == NULL)
        cree_racine_Patricia(&racine->fils[position]);

      insert_Patricia(racine->fils[position], temp);
      return;
    } else {
      // la valeur à insérer et la chaine gardée ont une partie en commun
      // calcul de la partie commune
      for (i = 0; i < indice; i++)
        commun[i] = racine->cle[position][i];
      commun[indice] = '\0';

      // calcul de temp : valeur = commun + temp
      j = indice;
      while (valeur[j] != '\0') {
        temp[j - indice] = valeur[j];
        j++;
      }
      temp[j - indice] = '\0';

      // calcul de reste : racine->cle[position] = commun + reste
      j = indice;
      while (racine->cle[position][j] != '\0') {
        reste[j - indice] = racine->cle[position][j];
        j++;
      }
      reste[j - indice] = '\0';

      // on crée un noeud supplémenatire avec 2 élements : temp et reste
      // on prend soin de ne rien perdre
      branche = racine->fils[position];
      cree_racine_Patricia(&racine->fils[position]);
      pos_bis = reste[0] - DEBUT;
      racine->fils[position]->cle[pos_bis] = malloc(TAILLE_MAX * sizeof(char));
      strcpy(racine->fils[position]->cle[pos_bis], reste);
      racine->fils[position]->fils[pos_bis] = branche;
      racine->fils[position]->fin[pos_bis] = racine->fin[position];
      racine->fin[position] = FALSE;
      strcpy(racine->cle[position], commun);
      if (strlen(temp) != 0) {
        insert_Patricia(racine->fils[position], temp);
      } else {
        racine->fin[position] = TRUE;
      }
      return;
    }
    return;
  }
  printf("fin insert");
}

int recherche_Patricia(ABR racine, char *valeur) {
  int i, indice, position;
  char reste[TAILLE_MAX];

  position = valeur[0] - DEBUT; // position de la première lettre

  // la chaine n'existe pas
  if (racine->cle[position] == NULL)
    return FALSE;

  // la chaine existe
  if (strcmp(racine->cle[position], valeur) == 0 &&
      racine->fin[position] == TRUE)
    return TRUE;

  indice = 0;
  while (racine->cle[position][indice] == valeur[indice])
    indice++; // on cherche la première différence

  // la valeur à chercher est plus petite que la chaine gardée
  // l'insertion est supposée correcte
  // => on conclue que la valeur n'existe pas
  if (racine->cle[position][indice] != '\0')
    return FALSE;

  // la valeur à chercher dépasse la chaine gardée
  if (racine->fils[position] == NULL)
    // la chaine gardée est finie et il n'y a pas de fils
    return FALSE;

  i = indice;
  while (valeur[i] != '\0') {
    reste[i - indice] = valeur[i];
    i++;
  }
  reste[i - indice] = '\0';

  // on continue la recherche dans le fils
  return recherche_Patricia(racine->fils[position], reste);
}



