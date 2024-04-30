import numpy as np
import binascii
import math


def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int(binascii.hexlify(text.encode(encoding, errors)), 16))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


def le1_bon_hashage(my_str, size):
    current = size
    n = len(my_str)
    toggle = True
    for x in range(len(my_str)):
        if toggle:
            current += ord(my_str[x])
        else:
            current *= ord(my_str[x])
        toggle = not toggle
    current = (current+n) % size
    return current


def le2_bon_hachage(string, taille_table_hash):
    # on utilise la place du caratère dans le mot et son code pour introduire une résistance à la permutation
    # on ajoute un poids plus important au premier et dernier caractère du mot
    # --> l'étalement est mieux pas pas idéal, on a encore bcp de collisions
    key = np.int32(0)
    first_char_code = ord(string[0])
    if string[-1] == '\n':  # saut de ligne à la fin du mot
        last_char_code = ord(string[-2])
        for i in range(len(string[0:-1])):
            caract = string[i]
            key += (i+1)*ord(caract)+first_char_code**(i+1) + last_char_code**(len(string)+1-i)
        return (np.int32(key % taille_table_hash))

    elif string[-1] != '\n':
        last_char_code = ord(string[-1])
        for i in range(len(string)):
            caract = string[i]
            key += (i+1)*ord(caract)+first_char_code**(i+1) + last_char_code**(len(string)+1-i)
        return (np.int32(key % taille_table_hash))

# Fonction originale


def le2_hachage_original(my_str, size):
    current = int(text_to_bits(my_str))
    # current est la chaine de caractère écrite en binaire puis convertie en int
    return current % size
# Ce qui est original, c'est le nombre de collision qui est plus petit
# pour une table de taille 707 658 contre une table de taille 1 887 088


def co1_hachage_original(chaine, taille_table_hachage):
    chaine = chaine.lower()
    xb = 0
    for i in range(0, len(chaine)):
        char = ord(chaine[i]) - 97
        xb += 26 ** (len(chaine) - i - 1) * char
    if (taille_table_hachage % 2) == 0:
        xb = xb % (taille_table_hachage - 1)
    else:
        xb = xb % taille_table_hachage
    return xb


def co1_bon_hachage(chaine, taille_table_hachage):
    h = 0
    for i in range(len(chaine)):
        char = ord(chaine[i]) - 97
        h += ~ (char << 5)
        h += (h << 15)
        h ^= ~ (h >> 3)
    h += (h << 3)
    h ^= (h >> 9)
    if (taille_table_hachage % 2) == 0:
        h = h % (taille_table_hachage - 1)
    else:
        h = h % taille_table_hachage
    return h


def al_hachage(mot, taille):
    d = mot.encode()
    lgt = len(d)
    indice = lgt-1
    cod = 0
    for i in d:
        cod += int(bin(i)[2:])*10000000**indice
        indice += -1
    cod = math.floor(cod+lgt) % taille
    return cod


def el1_bon_hachage(mot, size):  # meilleure fonction de hashage
    ind = size
    for x in range(len(mot)):
        if mot[x] in ["a", "e", "i", "o", "u", "y"]:  # si la lettre est une voyelle
            # le *x permet de faire intervenir la position des lettres, ce qui va differencier davantage 2 mots qui ont les memes lettres
            ind += ord(mot[x])*x
        else:
            ind *= ord(mot[x])*x  # ord renvoie la valeur ASCII du caractère
    ind = ind % size  # on prend le reste de la division par size pour pas que ind>size, cela est malheureusement source de collisions
    return (ind)


def el_autre_hachage(mot, size):  # fonction de hachage qui fonctionne mais moins efficace
    ind = size
    for i in range(0, len(mot)):
        # ord renvoie la valeur ASCII du caractère (comprise entre 0 et 255)
        ind = ind*i + ord(mot[i])
    ind = ind % size
    return (ind)
# multiplier à chaque fois par i permet de prendre en compte de l'ordre des lettres dans le mot.
