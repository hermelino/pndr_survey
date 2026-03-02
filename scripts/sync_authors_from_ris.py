#!/usr/bin/env python3
"""
Sincroniza campo 'autores' do approved_papers.ris para 2-2-papers.json

O problema: 2-2-papers.json tem autores incompletos comparado ao RIS original.
Solução: Atualizar o campo 'autores' em 2-2-papers.json com os dados do RIS.
"""

import json
import rispy
from pathlib import Path


def main():
    # Carregar RIS
    ris_path = Path(__file__).parent.parent / 'data' / '2-papers' / 'approved_papers.ris'
    with open(ris_path, 'r', encoding='utf-8') as f:
        ris_records = list(rispy.load(f))

    print(f"OK Carregados {len(ris_records)} registros do RIS")

    # Criar mapeamento DOI/label -> autores (do RIS)
    ris_authors_by_doi = {}
    ris_authors_by_label = {}

    for rec in ris_records:
        doi = rec.get('doi', '').strip()
        label = rec.get('label', '').strip()
        authors = rec.get('authors', [])

        if authors:
            # Juntar autores com ponto-e-vírgula
            authors_str = '; '.join(authors)

            if doi:
                ris_authors_by_doi[doi.lower()] = authors_str
            if label:
                ris_authors_by_label[label.lower()] = authors_str

    print(f"OK Mapeados {len(ris_authors_by_doi)} DOIs e {len(ris_authors_by_label)} labels com autores")

    # Carregar JSON
    json_path = Path(__file__).parent.parent / 'data' / '2-papers' / '2-2-papers.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    print(f"OK Carregados {len(json_data)} registros do JSON")

    # Atualizar autores nos registros aprovados
    updated = 0
    not_found = 0
    not_found_list = []

    for paper in json_data:
        if paper.get('triagem') == 'APROVADO':
            doi = paper.get('doi', '').strip().lower()
            label = paper.get('id_registro', '').strip().lower()

            new_authors = None

            # Tentar match por DOI primeiro
            if doi and doi in ris_authors_by_doi:
                new_authors = ris_authors_by_doi[doi]
            # Senão, tentar por label
            elif label and label in ris_authors_by_label:
                new_authors = ris_authors_by_label[label]

            if new_authors:
                old_authors = paper.get('autores', '')
                if old_authors != new_authors:
                    paper['autores'] = new_authors
                    updated += 1
                    print(f"  OK Atualizado: {paper.get('titulo', '')[:60]}...")
            else:
                not_found += 1
                not_found_list.append(paper.get('titulo', '')[:60])
                print(f"  WARN NAO ENCONTRADO no RIS: {paper.get('titulo', '')[:60]}...")

    print(f"\nOK Atualizados: {updated}")
    print(f"WARN Nao encontrados: {not_found}")

    # Salvar JSON atualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"\nSUCCESS Arquivo atualizado: {json_path}")


if __name__ == '__main__':
    main()
