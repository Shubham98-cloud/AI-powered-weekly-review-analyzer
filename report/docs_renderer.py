from typing import List
from .models import ReportPayload, Theme

def render_docs_markdown(payload: ReportPayload) -> str:
    """
    Render the report as a Markdown section for Google Docs.
    """
    md = []
    
    # Heading (will be used as the anchor in Google Docs)
    md.append(f"## {payload.iso_week} — {payload.product}")
    md.append("")
    
    # Metadata
    stars = "⭐" * int(round(payload.avg_rating))
    md.append(f"**Reviews analysed:** {payload.reviews_analysed} | **Clusters found:** {payload.clusters_found} | **Avg rating:** {stars} {payload.avg_rating:.1f}")
    md.append("")
    
    # Themes
    md.append("### 📊 Top Themes")
    md.append("")
    
    for i, theme in enumerate(payload.themes, 1):
        md.append(f"#### {i}. {theme.theme_name} ({theme.review_count} reviews · avg ⭐ {theme.avg_rating:.1f})")
        
        # Quotes
        for quote in theme.quotes:
            md.append(f"> \"{quote}\"")
        
        # Action Ideas
        if theme.action_ideas:
            md.append("")
            for idea in theme.action_ideas:
                md.append(f"💡 **Action:** {idea}")
        
        md.append("")
        
    # Stakeholder Insight Table
    md.append("### 🗂 Stakeholder Insights")
    md.append("| Audience | Key Insight |")
    md.append("|---|---|")
    
    # Basic logic for insights
    if any(t.avg_rating < 2.5 for t in payload.themes):
        md.append("| Product | Critical regressions detected in low-rating clusters |")
    else:
        md.append("| Product | General maintenance and sentiment tracking |")
        
    md.append("| Support | Use quotes above for canned responses to known issues |")
    md.append("| Leadership | Review the 'Action' points for priority roadmap alignment |")
    md.append("")
    
    return "\n".join(md)
