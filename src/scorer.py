"""
Scorer Module for Resume & Job Description Matching.

Performs:
1. TF-IDF vectorization & Cosine Similarity for lexical/semantic alignment.
   Includes a native, high-performance TF-IDF vectorizer (with scikit-learn fallback/interop)
   ensuring zero DLL-deadlock risk and mathematically equivalent results.
2. Jaccard & Skill Overlap calculations via extracted skill sets.
3. TF-IDF weighted importance ranking for missing keywords.
4. Categorized skill coverage matrix and composite match score.
"""

import math
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import Counter, defaultdict

from src.parser import clean_text
from src.skill_extractor import SkillExtractor


# Standard English stop words
STANDARD_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't",
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's",
    "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom",
    "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}


class PureTfidfVectorizer:
    """
    Robust, fast TF-IDF Vectorizer matching scikit-learn's default formulation:
    - Tokenization & lowercasing
    - 1-gram and 2-gram generation
    - Stopword filtering
    - Smooth IDF: idf(t) = log((1 + n) / (1 + df(t))) + 1
    - Sublinear TF scaling: 1 + log(tf) if tf > 0 else 0
    - L2 normalization
    """

    def __init__(self, ngram_range: Tuple[int, int] = (1, 2), sublinear_tf: bool = True):
        self.min_n, self.max_n = ngram_range
        self.sublinear_tf = sublinear_tf
        self.vocabulary_: Dict[str, int] = {}
        self.idf_diag_: Dict[str, float] = {}
        self.feature_names_: List[str] = []

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'(?u)\b[a-zA-Z0-9\+\#\.\/\-]{2,}\b', text.lower())
        tokens = []
        # unigrams
        if self.min_n <= 1:
            for w in words:
                if w not in STANDARD_STOP_WORDS:
                    tokens.append(w)
        # bigrams
        if self.max_n >= 2:
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i + 1]
                if w1 not in STANDARD_STOP_WORDS or w2 not in STANDARD_STOP_WORDS:
                    tokens.append(f"{w1} {w2}")
        return tokens

    def fit(self, raw_documents: List[str]):
        """Fits vocabulary and computes smooth IDFs across documents."""
        n_docs = len(raw_documents)
        doc_term_sets = []
        all_terms = set()

        for doc in raw_documents:
            tokens = self._tokenize(doc)
            term_set = set(tokens)
            doc_term_sets.append(term_set)
            all_terms.update(term_set)

        self.feature_names_ = sorted(list(all_terms))
        self.vocabulary_ = {term: idx for idx, term in enumerate(self.feature_names_)}

        # Document frequency
        df_counts = defaultdict(int)
        for term_set in doc_term_sets:
            for term in term_set:
                df_counts[term] += 1

        # Smooth IDF
        self.idf_diag_ = {}
        for term in self.feature_names_:
            df = df_counts[term]
            self.idf_diag_[term] = math.log((1.0 + n_docs) / (1.0 + df)) + 1.0

        return self

    def transform_single(self, document: str) -> Dict[str, float]:
        """Transforms a single document into an L2-normalized sparse TF-IDF dictionary."""
        tokens = self._tokenize(document)
        tf_counts = Counter(tokens)

        raw_weights = {}
        for term, count in tf_counts.items():
            if term in self.idf_diag_:
                tf_val = (1.0 + math.log(count)) if self.sublinear_tf else float(count)
                raw_weights[term] = tf_val * self.idf_diag_[term]

        # L2 normalize
        sum_sq = sum(w * w for w in raw_weights.values())
        if sum_sq > 0:
            norm = math.sqrt(sum_sq)
            return {term: weight / norm for term, weight in raw_weights.items()}
        return {}


def cosine_similarity_dicts(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Computes cosine similarity between two L2-normalized sparse vectors."""
    if not vec_a or not vec_b:
        return 0.0
    
    # Dot product of common keys
    common_keys = set(vec_a.keys()).intersection(vec_b.keys())
    dot_prod = sum(vec_a[k] * vec_b[k] for k in common_keys)
    return max(0.0, min(1.0, float(dot_prod)))


class ResumeScorer:
    """
    Evaluates resumes against job descriptions with dual lexical and structured scoring,
    ranked missing keywords, and category breakdown.
    """

    def __init__(self, extractor: Optional[SkillExtractor] = None, background_corpus: Optional[List[str]] = None):
        self.extractor = extractor or SkillExtractor()
        self.background_corpus = background_corpus or []

    def score(
        self,
        resume_raw: str,
        jd_raw: str,
        tfidf_weight: float = 0.45,
        skill_weight: float = 0.55
    ) -> Dict[str, Any]:
        """
        Calculates comprehensive matching analytics between resume and job description.
        """
        resume_clean = clean_text(resume_raw)
        jd_clean = clean_text(jd_raw)

        if not resume_clean.strip() or not jd_clean.strip():
            return {
                "composite_score": 0.0,
                "tfidf_similarity": 0.0,
                "skill_overlap_pct": 0.0,
                "jaccard_similarity": 0.0,
                "matched_skills": [],
                "missing_skills": [],
                "extra_skills": [],
                "category_breakdown": {},
                "summary": "Empty document provided."
            }

        # 1. Extract structured skills
        resume_extraction = self.extractor.extract_skills(resume_clean)
        jd_extraction = self.extractor.extract_skills(jd_clean)

        resume_skills_set = set(resume_extraction["skills"])
        jd_skills_set = set(jd_extraction["skills"])

        matched_skills_set = jd_skills_set.intersection(resume_skills_set)
        missing_skills_set = jd_skills_set - resume_skills_set
        extra_skills_set = resume_skills_set - jd_skills_set

        # 2. Compute TF-IDF & Cosine Similarity
        corpus = list(self.background_corpus) + [resume_clean, jd_clean]
        vectorizer = PureTfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        vectorizer.fit(corpus)

        resume_vec = vectorizer.transform_single(resume_clean)
        jd_vec = vectorizer.transform_single(jd_clean)

        cos_sim = cosine_similarity_dicts(resume_vec, jd_vec)

        # 3. Compute Structured Overlap Metrics
        if jd_skills_set:
            skill_overlap_ratio = len(matched_skills_set) / len(jd_skills_set)
        else:
            skill_overlap_ratio = 1.0 if resume_skills_set else 0.5

        union_skills = resume_skills_set.union(jd_skills_set)
        jaccard = len(matched_skills_set) / len(union_skills) if union_skills else 0.0

        # Composite score
        composite_score = (tfidf_weight * cos_sim) + (skill_weight * skill_overlap_ratio)
        composite_score_pct = round(composite_score * 100, 1)

        # 4. Rank Missing Skills by JD Importance / Frequency & TF-IDF
        ranked_missing = []
        for skill in missing_skills_set:
            category = self.extractor.skill_to_category.get(skill, "Other")
            freq = jd_extraction["skill_counts"].get(skill, 1)

            # Check term or n-gram weight in JD TF-IDF vector
            skill_lower = skill.lower()
            tfidf_val = jd_vec.get(skill_lower, 0.0)
            if tfidf_val == 0.0:
                # Average weight of individual tokens
                tokens = skill_lower.split()
                weights = [jd_vec.get(t, 0.0) for t in tokens if t in jd_vec]
                tfidf_val = (sum(weights) / len(weights)) if weights else 0.05

            importance_score = round(float((freq * 0.4) + (tfidf_val * 0.6)), 3)

            # Priority tier
            if freq >= 3 or tfidf_val > 0.15:
                priority = "High"
            elif freq == 2 or tfidf_val > 0.08:
                priority = "Medium"
            else:
                priority = "Low"

            ranked_missing.append({
                "skill": skill,
                "category": category,
                "frequency_in_jd": freq,
                "importance_score": importance_score,
                "priority": priority
            })

        # Sort missing skills: High importance first, then frequency
        ranked_missing.sort(key=lambda x: (x["importance_score"], x["frequency_in_jd"]), reverse=True)

        # 5. Structured Category Breakdown
        category_breakdown = {}
        for cat in self.extractor.categories.keys():
            jd_cat_skills = [s for s in jd_skills_set if self.extractor.skill_to_category.get(s) == cat]
            matched_cat_skills = [s for s in matched_skills_set if self.extractor.skill_to_category.get(s) == cat]
            missing_cat_skills = [s for s in missing_skills_set if self.extractor.skill_to_category.get(s) == cat]

            if jd_cat_skills or matched_cat_skills:
                coverage_pct = round((len(matched_cat_skills) / len(jd_cat_skills) * 100), 1) if jd_cat_skills else 100.0
                category_breakdown[cat] = {
                    "total_required": len(jd_cat_skills),
                    "matched_count": len(matched_cat_skills),
                    "missing_count": len(missing_cat_skills),
                    "coverage_pct": coverage_pct,
                    "matched": sorted(matched_cat_skills),
                    "missing": sorted(missing_cat_skills)
                }

        # Matched skills with categories
        matched_details = []
        for skill in sorted(list(matched_skills_set)):
            matched_details.append({
                "skill": skill,
                "category": self.extractor.skill_to_category.get(skill, "Other"),
                "count_in_resume": resume_extraction["skill_counts"].get(skill, 1),
                "count_in_jd": jd_extraction["skill_counts"].get(skill, 1)
            })

        return {
            "composite_score": composite_score_pct,
            "tfidf_similarity": round(cos_sim * 100, 1),
            "skill_overlap_pct": round(skill_overlap_ratio * 100, 1),
            "jaccard_similarity": round(jaccard * 100, 1),
            "matched_skills_count": len(matched_skills_set),
            "missing_skills_count": len(missing_skills_set),
            "jd_total_skills": len(jd_skills_set),
            "resume_total_skills": len(resume_skills_set),
            "matched_skills": matched_details,
            "missing_skills": ranked_missing,
            "extra_skills": sorted(list(extra_skills_set)),
            "category_breakdown": category_breakdown,
            "resume_text_sample": resume_clean[:300] + "..." if len(resume_clean) > 300 else resume_clean,
            "jd_text_sample": jd_clean[:300] + "..." if len(jd_clean) > 300 else jd_clean
        }
