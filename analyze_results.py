"""
Analysis and Visualization Tools
Generate charts and detailed analysis from benchmark results
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_results(csv_path: str) -> pd.DataFrame:
    """Load results CSV"""
    return pd.read_csv(csv_path)

def plot_model_comparison(df: pd.DataFrame, output_dir: Path = Path("./outputs")):
    """Compare models side by side"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # WER comparison
    model_wer = df.groupby('model')['wer'].mean().sort_values()
    model_wer.plot(kind='bar', ax=axes[0], color='steelblue')
    axes[0].set_title('Average Word Error Rate (WER) by Model')
    axes[0].set_ylabel('WER')
    axes[0].set_xlabel('Model')
    axes[0].set_ylim(0, 1)
    
    # CER comparison
    model_cer = df.groupby('model')['cer'].mean().sort_values()
    model_cer.plot(kind='bar', ax=axes[1], color='coral')
    axes[1].set_title('Average Character Error Rate (CER) by Model')
    axes[1].set_ylabel('CER')
    axes[1].set_xlabel('Model')
    axes[1].set_ylim(0, 1)
    
    # Entity Accuracy comparison
    model_entity = (df.groupby('model')['entity_correct'].sum() / df.groupby('model').size() * 100).sort_values(ascending=False)
    model_entity.plot(kind='bar', ax=axes[2], color='mediumseagreen')
    axes[2].set_title('Entity Extraction Accuracy by Model')
    axes[2].set_ylabel('Accuracy (%)')
    axes[2].set_xlabel('Model')
    axes[2].set_ylim(0, 100)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'model_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: model_comparison.png")
    plt.close()

def plot_condition_analysis(df: pd.DataFrame, output_dir: Path = Path("./outputs")):
    """Analyze performance by audio condition"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    conditions = df['condition'].unique()
    
    # WER by condition
    condition_wer = df.groupby('condition')['wer'].mean()
    condition_wer.plot(kind='bar', ax=axes[0, 0], color='steelblue')
    axes[0, 0].set_title('Average WER by Audio Condition')
    axes[0, 0].set_ylabel('WER')
    axes[0, 0].set_ylim(0, 1)
    
    # CER by condition
    condition_cer = df.groupby('condition')['cer'].mean()
    condition_cer.plot(kind='bar', ax=axes[0, 1], color='coral')
    axes[0, 1].set_title('Average CER by Audio Condition')
    axes[0, 1].set_ylabel('CER')
    axes[0, 1].set_ylim(0, 1)
    
    # Entity accuracy by condition
    condition_entity = (df.groupby('condition')['entity_correct'].sum() / df.groupby('condition').size() * 100)
    condition_entity.plot(kind='bar', ax=axes[1, 0], color='mediumseagreen')
    axes[1, 0].set_title('Entity Accuracy by Audio Condition')
    axes[1, 0].set_ylabel('Accuracy (%)')
    axes[1, 0].set_ylim(0, 100)
    
    # Box plot: WER distribution by condition
    df.boxplot(column='wer', by='condition', ax=axes[1, 1])
    axes[1, 1].set_title('WER Distribution by Condition')
    axes[1, 1].set_ylabel('WER')
    plt.suptitle('')  # Remove default title
    
    plt.tight_layout()
    fig.savefig(output_dir / 'condition_analysis.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: condition_analysis.png")
    plt.close()

def plot_locality_difficulty(df: pd.DataFrame, output_dir: Path = Path("./outputs"), top_n: int = 10):
    """Identify hardest and easiest localities"""
    locality_stats = df.groupby('locality').agg({
        'wer': 'mean',
        'entity_correct': 'mean'
    }).sort_values('wer', ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Top N hardest localities
    hardest = locality_stats.head(top_n)
    hardest['wer'].plot(kind='barh', ax=axes[0], color='lightcoral')
    axes[0].set_title(f'Top {top_n} Hardest Localities (by WER)')
    axes[0].set_xlabel('Average WER')
    axes[0].invert_yaxis()
    
    # Top N easiest localities
    easiest = locality_stats.tail(top_n)
    easiest['wer'].plot(kind='barh', ax=axes[1], color='lightgreen')
    axes[1].set_title(f'Top {top_n} Easiest Localities (by WER)')
    axes[1].set_xlabel('Average WER')
    axes[1].invert_yaxis()
    
    plt.tight_layout()
    fig.savefig(output_dir / 'locality_difficulty.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: locality_difficulty.png")
    plt.close()

def plot_model_x_condition_heatmap(df: pd.DataFrame, output_dir: Path = Path("./outputs")):
    """Heatmap: Model performance across conditions"""
    pivot_wer = df.pivot_table(values='wer', index='model', columns='condition', aggfunc='mean')
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot_wer, annot=True, fmt='.2%', cmap='RdYlGn_r', ax=ax, cbar_kws={'label': 'WER'})
    ax.set_title('Model Performance Across Audio Conditions (WER)')
    ax.set_xlabel('Audio Condition')
    ax.set_ylabel('Model')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'model_condition_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved: model_condition_heatmap.png")
    plt.close()

def generate_failure_report(df: pd.DataFrame, output_dir: Path = Path("./outputs"), top_n: int = 10):
    """Generate detailed failure analysis"""
    
    report_path = output_dir / 'failure_analysis.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("FAILURE ANALYSIS REPORT\n")
        f.write("="*80 + "\n\n")
        
        for model in df['model'].unique():
            model_df = df[df['model'] == model]
            failures = model_df[model_df['wer'] > 0.5].sort_values('wer', ascending=False)
            
            f.write(f"\n{model.upper()}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total samples: {len(model_df)}\n")
            f.write(f"Failures (WER > 50%): {len(failures)}\n")
            f.write(f"Average WER: {model_df['wer'].mean():.2%}\n")
            f.write(f"Entity Accuracy: {(model_df['entity_correct'].sum() / len(model_df) * 100):.1f}%\n\n")
            
            if len(failures) > 0:
                f.write(f"Top {min(top_n, len(failures))} Failures:\n")
                f.write("-" * 80 + "\n")
                
                for idx, (i, row) in enumerate(failures.head(top_n).iterrows(), 1):
                    f.write(f"\n{idx}. {row['filename']}\n")
                    f.write(f"   Condition: {row['condition']}\n")
                    f.write(f"   WER: {row['wer']:.2%} | CER: {row['cer']:.2%}\n")
                    f.write(f"   Expected: \"{row['expected']}\"\n")
                    f.write(f"   Got:      \"{row['transcription']}\"\n")
    
    print(f"✓ Saved: failure_analysis.txt")

def generate_summary_table(df: pd.DataFrame, output_dir: Path = Path("./outputs")):
    """Create summary table for report"""
    summary = []
    
    for model in sorted(df['model'].unique()):
        model_df = df[df['model'] == model]
        summary.append({
            'Model': model.upper(),
            'Samples': len(model_df),
            'Avg WER': f"{model_df['wer'].mean():.2%}",
            'Best WER': f"{model_df['wer'].min():.2%}",
            'Worst WER': f"{model_df['wer'].max():.2%}",
            'Avg CER': f"{model_df['cer'].mean():.2%}",
            'Entity Accuracy': f"{(model_df['entity_correct'].sum() / len(model_df) * 100):.1f}%",
        })
    
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(output_dir / 'summary_table.csv', index=False)
    
    print(f"\n✓ Saved: summary_table.csv")
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(summary_df.to_string(index=False))

def main(results_csv: str = None):
    """Run all visualizations"""
    
    # Find results file if not specified
    if not results_csv:
        output_dir = Path("./outputs")
        csv_files = list(output_dir.glob("benchmark_results_*.csv"))
        if not csv_files:
            print("❌ No benchmark results found in ./outputs/")
            return
        results_csv = str(sorted(csv_files)[-1])  # Use latest
        print(f"📂 Using: {results_csv}")
    
    output_dir = Path("./outputs")
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("GENERATING ANALYSIS AND VISUALIZATIONS")
    print("="*80)
    
    # Load data
    df = load_results(results_csv)
    print(f"\n✓ Loaded {len(df)} results")
    
    # Generate all visualizations
    print("\n📊 Generating visualizations...")
    plot_model_comparison(df, output_dir)
    plot_condition_analysis(df, output_dir)
    plot_locality_difficulty(df, output_dir)
    plot_model_x_condition_heatmap(df, output_dir)
    
    # Generate reports
    print("\n📋 Generating reports...")
    generate_failure_report(df, output_dir)
    generate_summary_table(df, output_dir)
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print("\nGenerated files in ./outputs/:")
    print("  - model_comparison.png")
    print("  - condition_analysis.png")
    print("  - locality_difficulty.png")
    print("  - model_condition_heatmap.png")
    print("  - failure_analysis.txt")
    print("  - summary_table.csv")

if __name__ == "__main__":
    import sys
    results_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(results_file)
