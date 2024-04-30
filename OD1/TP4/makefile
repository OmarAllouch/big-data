tt : patricia_trie.o construire_Patricia_trie_depuis_fichier.o
	gcc -o tt patricia_trie.o construire_Patricia_trie_depuis_fichier.o
patricia_trie.o : patricia_trie.c patricia_trie.h general.h
	gcc -c patricia_trie.c
construire_Patricia_trie_depuis_fichier.o : construire_Patricia_trie_depuis_fichier.c patricia_trie.h general.h
	gcc -c construire_Patricia_trie_depuis_fichier.c
