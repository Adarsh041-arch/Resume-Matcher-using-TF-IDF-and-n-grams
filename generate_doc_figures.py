"""
Generates high-resolution chart figures for the Word Project Report.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
IMAGES_DIR = os.path.join(DOCS_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

# Set clean styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 0.8


def generate_benchmark_chart():
    """Generates comparison chart for Rule-Based vs Statistical NER."""
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    
    categories = ['Precision', 'Recall', 'F1-Score']
    rule_based = [95.7, 97.8, 96.7]
    statistical_ner = [68.4, 38.2, 49.0]
    
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, rule_based, width, label='Rule-Based EntityRuler (Taxonomy)', color='#4F46E5', edgecolor='#3730A3')
    rects2 = ax.bar(x + width/2, statistical_ner, width, label='Off-the-Shelf Statistical NER', color='#94A3B8', edgecolor='#64748B')
    
    ax.set_ylabel('Performance Score (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Skill Extraction Benchmark: Rule-Based vs Generic Statistical NER', fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold', color='#334155')
    ax.set_ylim(0, 115)
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.set_axisbelow(True)
    
    # Value labels on top of bars
    def autolabel(rects, is_highlight=False):
        for rect in rects:
            height = rect.get_height()
            color = '#312E81' if is_highlight else '#475569'
            ax.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),  # 4 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10, fontweight='bold', color=color)
            
    autolabel(rects1, True)
    autolabel(rects2, False)
    
    plt.tight_layout()
    output_path = os.path.join(IMAGES_DIR, "benchmark_performance.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print("Saved benchmark_performance.png")


def generate_correlation_chart():
    """Generates correlation scatter plot: Model Composite Score vs Human Match Score."""
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=300)
    
    pairs = [
        ("Data Scientist Match", 0.95, 0.485, '#10B981'),
        ("DevOps Match", 0.92, 0.603, '#10B981'),
        ("Backend Match", 0.90, 0.545, '#10B981'),
        ("Backend vs DevOps (Partial)", 0.40, 0.250, '#F59E0B'),
        ("Backend vs DS (Partial)", 0.35, 0.180, '#F59E0B'),
        ("DevOps vs DS (Mismatch)", 0.15, 0.150, '#EF4444'),
        ("DS vs DevOps (Mismatch)", 0.20, 0.277, '#EF4444')
    ]
    
    human_scores = [p[1] * 100 for p in pairs]
    model_scores = [p[2] * 100 for p in pairs]
    colors = [p[3] for p in pairs]
    
    # Scatter plot
    for i, p in enumerate(pairs):
        ax.scatter(human_scores[i], model_scores[i], s=140, color=colors[i], edgecolors='#1E293B', linewidth=1.5, zorder=5, label=p[0])
    
    # Linear fit trendline
    z = np.polyfit(human_scores, model_scores, 1)
    p_fit = np.poly1d(z)
    x_vals = np.linspace(10, 100, 100)
    ax.plot(x_vals, p_fit(x_vals), linestyle='--', color='#4F46E5', linewidth=2, label='Linear Trendline (r = 0.937)', zorder=3)
    
    ax.set_xlabel('Human Ground-Truth Match Quality (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_ylabel('Model Composite Match Score (%)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Model Alignment: Spearman Correlation rs = 0.786, Pearson r = 0.937', fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.grid(True, linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.set_xlim(5, 105)
    ax.set_ylim(5, 75)
    
    # Add annotations for a few key points
    ax.annotate('Target Matches (High Alignment)', xy=(92, 58), xytext=(55, 68),
                arrowprops=dict(arrowstyle="->", color='#10B981', lw=1.5),
                fontsize=9.5, fontweight='bold', color='#065F46',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#ECFDF5', edgecolor='#A7F3D0'))

    ax.annotate('Domain Mismatches', xy=(18, 20), xytext=(22, 10),
                arrowprops=dict(arrowstyle="->", color='#EF4444', lw=1.5),
                fontsize=9.5, fontweight='bold', color='#991B1B',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#FEF2F2', edgecolor='#FECACA'))
    
    plt.tight_layout()
    output_path = os.path.join(IMAGES_DIR, "correlation_scatter.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print("Saved correlation_scatter.png")


def generate_category_coverage_chart():
    """Generates radar or grouped category coverage breakdown."""
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    
    categories = ['Languages', 'Frameworks', 'Cloud & DevOps', 'Databases', 'AI & ML', 'Methodologies']
    target_demands = [4, 7, 5, 4, 11, 4]
    matched_skills = [3, 6, 2, 2, 8, 3]
    
    x = np.arange(len(categories))
    width = 0.35
    
    r1 = ax.bar(x - width/2, target_demands, width, label='Skills Demanded in Job Description', color='#0284C7')
    r2 = ax.bar(x + width/2, matched_skills, width, label='Skills Matched on Resume', color='#10B981')
    
    ax.set_ylabel('Number of Unique Skills', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Category Skill Coverage: Senior Data Scientist Scenario', fontsize=13, fontweight='bold', pad=15, color='#0F172A')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10, fontweight='bold', color='#334155', rotation=15)
    ax.legend(frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0')
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#CBD5E1')
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_path = os.path.join(IMAGES_DIR, "category_coverage.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    print("Saved category_coverage.png")


def main():
    generate_benchmark_chart()
    generate_correlation_chart()
    generate_category_coverage_chart()


if __name__ == "__main__":
    main()
