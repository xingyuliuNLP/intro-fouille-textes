#! /usr/bin/env python3

import argparse
import pathlib
import re
import sys

from collections import Counter


def _process(class_dirs, mots_vides, boolean=False, lexicon=None):
    contents = {d.name: [bag_of_words(f, mots_vides) for f in files]
                for d, files in class_dirs}
    if lexicon is None:
        lexicon = sorted(set(w
                             for bows in contents.values()
                             for b in bows
                             for w in b.keys()
                             if w and w not in mots_vides))
    class_names = sorted(contents.keys())
    return (lexicon,
            class_names,
            ([*vec(b, lexicon, boolean), c] for c in class_names for b in contents[c]))


def nettoyage(texte):
    texte = re.sub(r"[&%!?\|\"{\(\[|_\)\]},\.;/:§»«”“‘…–—−]", '', texte)
    texte = re.sub(r'\d', '', texte)
    texte = texte.replace("’", "'")
    texte = texte.replace("'", "' ")
    return texte


def bag_of_words(nom_fichier, mots_vides):
    with open(nom_fichier) as fichier:
        text = fichier.read()
    text = nettoyage(text)
    return Counter(w.lower()
                   for w in re.split(r"[\s\.]+", text)
                   for l in (w.lower(),)
                   if w and w not in mots_vides)


def vec(bow, lexicon, boolean):
    vecteur = [bow.get(m, 0) for m in lexicon]
    if boolean:
        vecteur = [1 if v else 0 for v in vecteur]
    return vecteur


def process(corpus_path, out_path=None, boolean=False, fichier_mots_vides=None, lexicon=None):
    dossier = pathlib.Path(corpus_path)
    if out_path is None:
        out_path = dossier.parent/'fichier-resultat.arff'
    if fichier_mots_vides is None:
        mots_vides = []
    else:
        with open(fichier_mots_vides) as in_stream:
            mots_vides = set(l.strip() for l in in_stream)
    if lexicon is not None:
        with open(fichier_mots_vides) as in_stream:
            lexicon = sorted(set(l.strip() for l in in_stream))
    # Chaque sous-dossier (non-caché) du dossier principal est une étiquette de classe
    class_dirs = ((d, sorted(d.glob("*.txt")))
                  for d in dossier.iterdir()
                  if d.is_dir and not d.name.startswith('.'))
    lexicon, class_names, rows = _process(class_dirs, mots_vides, boolean, lexicon)

    # Écriture des donnees au format .arff dans la variable `sortie`
    sortie = ['@relation corpus']
    for mot in lexicon:
        sortie.append("@attribute '{m}' numeric".format(m=mot.replace("'", r"\'")))
    sortie.append(f"@attribute 'classe' {{{','.join(class_names)}}}")
    sortie.append("@data")
    for r in rows:
        sortie.append(','.join(map(str, r)))

    # ecriture du contenu de la variable dans le fichier de sortie
    with open(out_path, 'w') as fichier_sortie:
        fichier_sortie.write('\n'.join(sortie))

    print('fichier-resultat.arff produit !')


def main_entry_point(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv:
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('corpus_path', metavar='dossier_corpus', type=str,
                            help='Le dossier contenant le corpus (un sous-dossier par étiquette)')
        parser.add_argument('out_path', metavar='fichier_sortie',
                            nargs='?', type=str, default=None,
                            help='Le chemin du fichier de sortie')
        parser.add_argument('--mots-vides', metavar='fichier_mots_vides', type=str, default=None,
                            help='Un fichier contenant une liste de mots vides (un par ligne)')
        parser.add_argument('--lexicon', metavar='fichier_lexique', type=str, default=None,
                            help='Un fichier contenant un lexique (un mot par ligne)')
        parser.add_argument('--boolean', action='store_true',
                            help='Utiliser des représentations booléennes')

        args = parser.parse_args(argv)
        return process(args.corpus_path, args.out_path, args.boolean, args.mots_vides, args.lexicon)

    # Legacy interactive mode
    print('Mode interactif (legacy). Utiliser `vectorisation.py -h` pour le mode CLI.`')
    corpus_path = input("Nom du dossier contenant le corpus : ")
    fichier_mots_vides = input("Nom du fichier de mots vides (se terminant par .txt) : ")

    choix = None
    while choix not in ('1', '2'):
        choix = input("Représentation booléenne (taper 1) ou en nombre d'occurrences (taper 2) ? ")
    process(corpus_path, boolean=choix == 1, fichier_mots_vides=fichier_mots_vides)


if __name__ == '__main__':
    sys.exit(main_entry_point(sys.argv[1:]))
