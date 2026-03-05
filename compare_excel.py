"""Compare two Excel classification files and report all differences.

Compares all_papers_llm_classif.xlsx (original) vs all_papers_llm_classif_final.xlsx (updated).
Focuses on rejection-related changes but reports ALL column-level differences.
"""

import pandas as pd
import sys
import io
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = Path(r"c:\OneDrive\github\pndr_survey\data\2-papers")
ORIG = BASE / "_temp_orig.xlsx"
FINAL = BASE / "_temp_final.xlsx"

# Key identification columns
ID_COLS = ["#", "Titulo", "Autores", "Ano", "Arquivo PDF"]

# Columns that signal rejection / screening changes
SCREENING_COLS = ["Triagem", "Motivo Exclusão"]


def normalize(val: object) -> str:
    """Normalize a cell value for comparison (NaN -> '', strip whitespace)."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def main() -> None:
    df_orig = pd.read_excel(ORIG)
    df_final = pd.read_excel(FINAL)

    # Fix encoding issue with column names
    orig_cols = list(df_orig.columns)
    final_cols = list(df_final.columns)

    print("=" * 90)
    print("COMPARISON REPORT: all_papers_llm_classif.xlsx vs all_papers_llm_classif_final.xlsx")
    print("=" * 90)
    print(f"Original:  {df_orig.shape[0]} rows x {df_orig.shape[1]} cols")
    print(f"Final:     {df_final.shape[0]} rows x {df_final.shape[1]} cols")
    print()

    # Columns only in final
    new_cols = [c for c in final_cols if c not in orig_cols]
    if new_cols:
        print(f"NEW COLUMNS in final (not in original): {new_cols}")
        print()

    # Columns only in original
    removed_cols = [c for c in orig_cols if c not in final_cols]
    if removed_cols:
        print(f"REMOVED COLUMNS (in original but not in final): {removed_cols}")
        print()

    # Common columns for comparison
    common_cols = [c for c in orig_cols if c in final_cols]

    # Match rows by index (both have 118 rows)
    assert len(df_orig) == len(df_final), (
        f"Row count mismatch: {len(df_orig)} vs {len(df_final)}"
    )

    # -------------------------------------------------------------------
    # 1. SCREENING / REJECTION CHANGES (priority report)
    # -------------------------------------------------------------------
    # Find the actual column name for "Motivo Exclusão" (may have encoding quirk)
    triagem_col = "Triagem"
    motivo_col = None
    for c in common_cols:
        if "Motivo" in c or "Exclus" in c:
            motivo_col = c
            break

    screening_changes: list[dict] = []
    for i in range(len(df_orig)):
        orig_triagem = normalize(df_orig.at[i, triagem_col])
        final_triagem = normalize(df_final.at[i, triagem_col])
        orig_motivo = normalize(df_orig.at[i, motivo_col]) if motivo_col else ""
        final_motivo = normalize(df_final.at[i, motivo_col]) if motivo_col else ""

        if orig_triagem != final_triagem or orig_motivo != final_motivo:
            screening_changes.append({
                "row": i,
                "#": df_orig.at[i, "#"],
                "pdf": df_orig.at[i, "Arquivo PDF"],
                "titulo": str(df_orig.at[i, "Titulo"])[:80],
                "autores": str(df_orig.at[i, "Autores"])[:60],
                "ano": df_orig.at[i, "Ano"],
                "orig_triagem": orig_triagem,
                "final_triagem": final_triagem,
                "orig_motivo": orig_motivo,
                "final_motivo": final_motivo,
            })

    print("=" * 90)
    print(f"SCREENING / REJECTION CHANGES  ({len(screening_changes)} papers)")
    print("=" * 90)

    new_rejections = []
    new_approvals = []
    motivo_only_changes = []

    for ch in screening_changes:
        if ch["orig_triagem"] != ch["final_triagem"]:
            if ch["final_triagem"] == "REJEITADO":
                new_rejections.append(ch)
            elif ch["final_triagem"] == "APROVADO":
                new_approvals.append(ch)
            else:
                # Other status change
                new_rejections.append(ch)  # group with rejections for now
        else:
            motivo_only_changes.append(ch)

    if new_rejections:
        print()
        print(f"--- NEW REJECTIONS (status changed TO REJEITADO): {len(new_rejections)} ---")
        for ch in new_rejections:
            print()
            print(f"  Row #{ch['#']}  |  {ch['pdf']}")
            print(f"  Title:   {ch['titulo']}")
            print(f"  Authors: {ch['autores']}")
            print(f"  Year:    {ch['ano']}")
            print(f"  Triagem: {ch['orig_triagem']!r}  -->  {ch['final_triagem']!r}")
            print(f"  Motivo:  {ch['orig_motivo']!r}  -->  {ch['final_motivo']!r}")

    if new_approvals:
        print()
        print(f"--- NEW APPROVALS (status changed TO APROVADO): {len(new_approvals)} ---")
        for ch in new_approvals:
            print()
            print(f"  Row #{ch['#']}  |  {ch['pdf']}")
            print(f"  Title:   {ch['titulo']}")
            print(f"  Authors: {ch['autores']}")
            print(f"  Year:    {ch['ano']}")
            print(f"  Triagem: {ch['orig_triagem']!r}  -->  {ch['final_triagem']!r}")
            print(f"  Motivo:  {ch['orig_motivo']!r}  -->  {ch['final_motivo']!r}")

    if motivo_only_changes:
        print()
        print(f"--- MOTIVO EXCLUSAO CHANGED (status unchanged): {len(motivo_only_changes)} ---")
        for ch in motivo_only_changes:
            print()
            print(f"  Row #{ch['#']}  |  {ch['pdf']}")
            print(f"  Title:   {ch['titulo']}")
            print(f"  Status:  {ch['final_triagem']}")
            print(f"  Motivo:  {ch['orig_motivo']!r}  -->  {ch['final_motivo']!r}")

    # -------------------------------------------------------------------
    # 2. ALL OTHER COLUMN CHANGES (non-screening, shared columns only)
    # -------------------------------------------------------------------
    print()
    print("=" * 90)
    print("ALL OTHER COLUMN-LEVEL CHANGES (shared columns, excluding new-only columns)")
    print("=" * 90)

    # Exclude screening cols already reported; also exclude new-only cols
    compare_cols = [c for c in common_cols if c not in [triagem_col, motivo_col]]

    other_changes: list[dict] = []
    for i in range(len(df_orig)):
        row_diffs: list[tuple[str, str, str]] = []
        for col in compare_cols:
            ov = normalize(df_orig.at[i, col])
            fv = normalize(df_final.at[i, col])
            if ov != fv:
                row_diffs.append((col, ov, fv))
        if row_diffs:
            other_changes.append({
                "row": i,
                "#": df_orig.at[i, "#"],
                "pdf": df_orig.at[i, "Arquivo PDF"],
                "titulo": str(df_orig.at[i, "Titulo"])[:80],
                "diffs": row_diffs,
            })

    print(f"\nPapers with non-screening changes in shared columns: {len(other_changes)}")

    for ch in other_changes:
        print()
        print(f"  Row #{ch['#']}  |  {ch['pdf']}")
        print(f"  Title: {ch['titulo']}")
        for col, ov, fv in ch["diffs"]:
            ov_short = ov[:120] + ("..." if len(ov) > 120 else "")
            fv_short = fv[:120] + ("..." if len(fv) > 120 else "")
            print(f"    [{col}]")
            print(f"      OLD: {ov_short!r}")
            print(f"      NEW: {fv_short!r}")

    # -------------------------------------------------------------------
    # 3. SUMMARY
    # -------------------------------------------------------------------
    print()
    print("=" * 90)
    print("SUMMARY")
    print("=" * 90)

    # Count final statuses
    triagem_counts_orig = df_orig[triagem_col].value_counts(dropna=False)
    triagem_counts_final = df_final[triagem_col].value_counts(dropna=False)

    print("\nTriagem distribution (ORIGINAL):")
    for status, count in triagem_counts_orig.items():
        print(f"  {status!r}: {count}")

    print("\nTriagem distribution (FINAL):")
    for status, count in triagem_counts_final.items():
        print(f"  {status!r}: {count}")

    print(f"\nTotal screening changes:  {len(screening_changes)}")
    print(f"  - New rejections:       {len(new_rejections)}")
    print(f"  - New approvals:        {len(new_approvals)}")
    print(f"  - Motivo-only changes:  {len(motivo_only_changes)}")
    print(f"Total other-col changes:  {len(other_changes)}")
    print(f"New columns added:        {len(new_cols)}")


if __name__ == "__main__":
    main()
