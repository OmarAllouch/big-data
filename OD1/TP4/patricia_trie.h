/* taille de l'alphabet */
# define NALPHABET 26
# define DEBUT 'a'
# define TAILLE_MAX 30

/* le type d'un noeud de Patricia TRIE */
struct noeud {
	char* cle[NALPHABET]; /* un tableau de pointeurs vers des chaine de caractères */
	short int fin[NALPHABET];
	struct noeud* fils[NALPHABET];
};

typedef struct noeud* ABR; /* ABR est le nom du type pointeur */	

void cree_racine_Patricia(ABR *racine); 
void affiche_Patricia(ABR racine);
void affiche_rec(ABR racine, char *partie_haute, int est_fin);
int recherche_Patricia(ABR racine, char *valeur);
void insert_Patricia(ABR racine, char *valeur);
