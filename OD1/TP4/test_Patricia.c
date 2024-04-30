#include "general.h"
#include "patricia_trie.h"
#include <stdio.h>

int main() {
  ABR mon_Patricia;

  cree_racine_Patricia(&mon_Patricia);
  affiche_Patricia(mon_Patricia);
  insert_Patricia(mon_Patricia, "chat");
  insert_Patricia(mon_Patricia, "ornithorinque");
  insert_Patricia(mon_Patricia, "toutou");
  insert_Patricia(mon_Patricia, "toutounet");
  insert_Patricia(mon_Patricia, "toutous");
  insert_Patricia(mon_Patricia, "chaton");
  insert_Patricia(mon_Patricia, "chattes");
  insert_Patricia(mon_Patricia, "toutoudemamie");
  insert_Patricia(mon_Patricia, "chasseur");
  printf(" Fin insertions.\n");
  affiche_Patricia(mon_Patricia);
}

