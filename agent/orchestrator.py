import sys
import json
import os
import asyncio
from datetime import datetime
from typing import List, Dict

# Relative imports
from ingestion import fetch_reviews
from nlp.pii_scrubber import scrub_reviews
from nlp.heuristics import filter_by_heuristics
from nlp.embeddings import embed_reviews
from nlp.clustering import cluster_embeddings
from nlp.summarizer import generate_themes
from nlp.validator import validate_quotes
from report.builder import build_report_payload
from report.docs_renderer import render_docs_markdown
from report.email_renderer import render_email_html
from delivery_mcp.docs import deliver_to_google_docs
from delivery_mcp.gmail import deliver_to_gmail
from audit.store import AuditStore
from config.loader import load_config, ConfigError

async def run_delivery_async(p_cfg, payload, markdown_content, html_content, settings):
    """Handles the asynchronous MCP delivery."""
    success_docs = False
    success_gmail = False
    
    if settings.delivery.google_docs.enabled:
        success_docs = await deliver_to_google_docs(
            markdown_content=markdown_content,
            doc_id=p_cfg.google_doc_id,
            mcp_config=settings.delivery.google_docs.mcp.dict()
        )
        
    if settings.delivery.gmail.enabled:
        subject = f"Weekly Pulse Report: {p_cfg.name} ({payload.iso_week})"
        success_gmail = await deliver_to_gmail(
            html_content=html_content,
            subject=subject,
            recipient=p_cfg.recipients[0],
            mcp_config=settings.delivery.gmail.mcp.dict()
        )
    
    return success_docs, success_gmail

def run_full_agent(product=None, week=None, dry_run=False):
    """
    The main production loop of the AI Agent.
    """
    print(f"--- Phase 6: Full AI Agent Orchestration ---")
    
    audit = AuditStore()
    
    try:
        products_cfg, settings_cfg = load_config()
    except ConfigError as e:
        print(f"Configuration Error: {e}")
        return
        
    current_week = week if week else datetime.now().strftime("%G-W%V")
    target_products = products_cfg.products
    if product:
        target_products = [p for p in target_products if p.name.lower() == product.lower()]
        
    for p_cfg in target_products:
        print(f"\n[RUN] Processing {p_cfg.name} for {current_week}...")
        
        # 1. Idempotency Check
        if not dry_run and audit.is_delivered(p_cfg.name, current_week):
            print(f"--- Already delivered for {p_cfg.name} in {current_week}. Skipping.")
            continue

        # 2. Ingestion
        reviews = fetch_reviews(p_cfg.name, p_cfg.appstore_id, p_cfg.playstore_id, settings_cfg.ingestion.window_weeks)
        if not reviews:
            print(f"[SKIP] No reviews found for {p_cfg.name}.")
            continue
            
        # 3. Filtering & PII
        scrubbed = scrub_reviews(reviews)
        substantive = filter_by_heuristics(scrubbed)
        if not substantive:
            print(f"[SKIP] No substantive reviews left for {p_cfg.name}.")
            continue
        
        # 4. NLP Reasoning (Gemini + Groq)
        try:
            embeddings = embed_reviews(substantive)
            labels = cluster_embeddings(embeddings, settings_cfg.nlp.umap.dict(), settings_cfg.nlp.hdbscan.dict())
            
            clusters: Dict[int, List] = {}
            for label, r in zip(labels, substantive):
                if label not in clusters: clusters[label] = []
                clusters[label].append(r)
                
            # Lenient clustering fallback
            if len(clusters) <= (1 if -1 in clusters else 0):
                labels = cluster_embeddings(embeddings, settings_cfg.nlp.umap.dict(), {"min_cluster_size": 3, "min_samples": 1})
                clusters = {label: [r for l, r in zip(labels, substantive) if l == label] for label in set(labels)}

            themes = generate_themes(clusters, model=settings_cfg.nlp.llm.primary_model)
            validated_themes = validate_quotes(themes, substantive)
        except Exception as e:
            print(f"ERROR: NLP Reasoning failed for {p_cfg.name}: {e}")
            continue

        # 5. Report Building
        payload = build_report_payload(p_cfg.name, current_week, substantive, validated_themes)
        markdown_content = render_docs_markdown(payload)
        html_content = render_email_html(payload)
        
        # 6. Delivery & Audit
        if dry_run:
            print(f"[DRY RUN] Would deliver to {p_cfg.google_doc_id} and {p_cfg.recipients[0]}")
        else:
            s_docs, s_gmail = asyncio.run(run_delivery_async(p_cfg, payload, markdown_content, html_content, settings_cfg))
            
            if s_docs or s_gmail:
                audit.log_run(p_cfg.name, current_week, status="delivered")
                print(f"SUCCESS: Delivery complete for {p_cfg.name}.")
            else:
                print(f"FAILED: Delivery FAILED for {p_cfg.name}.")

    print(f"\nAgent run complete.")

if __name__ == "__main__":
    run_full_agent()
