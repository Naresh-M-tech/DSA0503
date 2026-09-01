"""
Fuzzy Matcher Module
Uses RapidFuzz to identify inconsistently entered student names.
"""
import pandas as pd
from rapidfuzz import fuzz, process
from typing import List, Dict, Tuple


def find_fuzzy_matches(
    names: List[str],
    threshold: float = 85.0,
    max_matches: int = 500,
) -> List[Dict]:
    """Find pairs of names that are similar but not identical.

    Args:
        names: List of unique names to compare
        threshold: Minimum similarity score (0-100) to consider a match
        max_matches: Maximum number of matches to return

    Returns:
        List of dictionaries with original name, possible match, and similarity score
    """
    unique_names = list(set(n for n in names if pd.notna(n) and isinstance(n, str) and n.strip()))
    unique_names = [n for n in unique_names if len(n) > 1]

    matches = []
    seen_pairs = set()

    for i, name in enumerate(unique_names):
        # Find similar names using token_sort_ratio (handles word order differences)
        results = process.extract(
            name,
            unique_names[:i] + unique_names[i + 1:],
            scorer=fuzz.token_sort_ratio,
            limit=5,
        )

        for match_name, score, _ in results:
            if score >= threshold:
                pair = tuple(sorted([name, match_name]))
                if pair not in seen_pairs:
                    seen_pairs.add(pair)
                    matches.append({
                        "Original Name": name,
                        "Possible Match": match_name,
                        "Similarity": round(score, 1),
                    })

                if len(matches) >= max_matches:
                    break

        if len(matches) >= max_matches:
            break

    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x["Similarity"], reverse=True)
    return matches


def apply_fuzzy_matching(
    df: pd.DataFrame,
    threshold: float = 85.0,
    standardize_map: Dict[str, str] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Apply fuzzy matching to standardize names in a DataFrame.

    Args:
        df: DataFrame containing a 'Name' column
        threshold: Minimum similarity for matching
        standardize_map: Optional mapping of {variant: canonical_name}

    Returns:
        Tuple of (DataFrame with standardized names, fuzzy matching report)
    """
    if df is None or df.empty or "Name" not in df.columns:
        return df, pd.DataFrame()

    df_clean = df.copy()
    names = df_clean["Name"].dropna().unique().tolist()

    # Find fuzzy matches
    matches = find_fuzzy_matches(names, threshold=threshold)

    if not matches:
        return df_clean, pd.DataFrame()

    report_df = pd.DataFrame(matches)

    # Apply standardization if a map is provided
    if standardize_map:
        df_clean["Name"] = df_clean["Name"].map(
            lambda x: standardize_map.get(x, x) if pd.notna(x) else x
        )

    return df_clean, report_df


def create_standardization_map(matches: List[Dict]) -> Dict[str, str]:
    """Create a standardization map from fuzzy matches.

    For each pair, select the more common/longer name as the canonical form.
    """
    canonical_map = {}

    # Group by canonical candidates
    for match in matches:
        name1 = match["Original Name"]
        name2 = match["Possible Match"]
        similarity = match["Similarity"]

        if name1 in canonical_map:
            continue
        if name2 in canonical_map:
            continue

        # Pick the longer name as canonical (likely more correct)
        if len(name1) >= len(name2):
            canonical_map[name2] = name1
        else:
            canonical_map[name1] = name2

    return canonical_map
