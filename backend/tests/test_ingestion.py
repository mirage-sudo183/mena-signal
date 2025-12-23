"""Tests for ingestion module."""
import pytest
from datetime import datetime
from app.services.ingestion import (
    create_item_hash,
    determine_item_type,
    extract_company_name,
    extract_funding_details,
)
from app.models import ItemType


class TestCreateItemHash:
    """Tests for hash generation."""
    
    def test_same_inputs_same_hash(self):
        """Same inputs should produce same hash."""
        url = "https://example.com/article/123"
        title = "Test Article"
        published_at = datetime(2024, 1, 1, 12, 0, 0)
        
        hash1 = create_item_hash(url, title, published_at)
        hash2 = create_item_hash(url, title, published_at)
        
        assert hash1 == hash2
    
    def test_different_urls_different_hash(self):
        """Different URLs should produce different hashes."""
        title = "Test Article"
        published_at = datetime(2024, 1, 1)
        
        hash1 = create_item_hash("https://example.com/a", title, published_at)
        hash2 = create_item_hash("https://example.com/b", title, published_at)
        
        assert hash1 != hash2
    
    def test_url_normalization(self):
        """URL should be normalized (trailing slash, case)."""
        title = "Test Article"
        
        hash1 = create_item_hash("https://Example.com/Article/", title, None)
        hash2 = create_item_hash("https://example.com/article", title, None)
        
        assert hash1 == hash2
    
    def test_none_published_at(self):
        """Should handle None published_at."""
        hash1 = create_item_hash("https://example.com/a", "Title", None)
        assert hash1 is not None
        assert len(hash1) == 64  # SHA256 hex length


class TestDetermineItemType:
    """Tests for item type determination."""
    
    def test_funding_keywords_in_title(self):
        """Should detect funding from title keywords."""
        assert determine_item_type("Company raises $10M Series A", "", None) == ItemType.FUNDING
        assert determine_item_type("Startup secures seed funding", "", None) == ItemType.FUNDING
        assert determine_item_type("AI Company valued at $1B", "", None) == ItemType.FUNDING
    
    def test_funding_keywords_in_summary(self):
        """Should detect funding from summary keywords."""
        assert determine_item_type(
            "Company News",
            "The company raised $5 million in a Series A round",
            None
        ) == ItemType.FUNDING
    
    def test_funding_category(self):
        """Should respect category hint."""
        assert determine_item_type("New Product Launch", "", "funding") == ItemType.FUNDING
    
    def test_default_to_company(self):
        """Should default to company when no funding signals."""
        assert determine_item_type("New AI Assistant Launch", "", None) == ItemType.COMPANY
        assert determine_item_type("Product Update", "New features released", None) == ItemType.COMPANY


class TestExtractCompanyName:
    """Tests for company name extraction."""
    
    def test_raises_pattern(self):
        """Should extract company before 'raises'."""
        assert extract_company_name("Acme Corp raises $10M") == "Acme Corp"
        assert extract_company_name("OpenAI raises new round") == "OpenAI"
    
    def test_announces_pattern(self):
        """Should extract company before 'announces'."""
        assert extract_company_name("Google announces new AI") == "Google"
    
    def test_comma_pattern(self):
        """Should extract company before comma."""
        assert extract_company_name("Stripe, the payments company") == "Stripe"
    
    def test_fallback_to_first_words(self):
        """Should fallback to first words."""
        name = extract_company_name("Some Company Name")
        assert name is not None


class TestExtractFundingDetails:
    """Tests for funding details extraction."""
    
    def test_extract_series_round(self):
        """Should extract Series round type."""
        details = extract_funding_details("Company raises Series A", "")
        assert details['round_type'] == "series_a"
        
        details = extract_funding_details("Company closes Series B round", "")
        assert details['round_type'] == "series_b"
    
    def test_extract_seed_round(self):
        """Should extract seed round type."""
        details = extract_funding_details("Startup secures seed funding", "")
        assert details['round_type'] == "seed"
    
    def test_extract_amount_millions(self):
        """Should extract amount in millions."""
        details = extract_funding_details("Company raises $10 million", "")
        assert details['amount_usd'] == 10_000_000
        
        details = extract_funding_details("$5.5M funding round", "")
        assert details['amount_usd'] == 5_500_000
    
    def test_missing_details(self):
        """Should handle missing details gracefully."""
        details = extract_funding_details("Company news update", "")
        assert details['round_type'] is None
        assert details['amount_usd'] is None

