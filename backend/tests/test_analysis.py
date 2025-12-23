"""Tests for analysis module."""
import pytest
from app.services.analysis import get_stub_analysis


class TestStubAnalysis:
    """Tests for stub MENA analysis."""
    
    def test_stub_returns_valid_structure(self):
        """Stub should return valid analysis structure."""
        result = get_stub_analysis()
        
        assert 'fit_score' in result
        assert 'mena_summary' in result
        assert 'rubric' in result
    
    def test_stub_score_in_range(self):
        """Stub score should be in valid range."""
        result = get_stub_analysis()
        
        assert 0 <= result['fit_score'] <= 100
    
    def test_stub_summary_not_empty(self):
        """Stub summary should not be empty."""
        result = get_stub_analysis()
        
        assert result['mena_summary']
        assert len(result['mena_summary']) > 10
    
    def test_stub_rubric_has_all_dimensions(self):
        """Stub rubric should have all required dimensions."""
        result = get_stub_analysis()
        rubric = result['rubric']
        
        required_keys = [
            'budget_buyer_exists',
            'localization_arabic_bilingual',
            'regulatory_friction',
            'distribution_path',
            'time_to_revenue',
        ]
        
        for key in required_keys:
            assert key in rubric
            assert 0 <= rubric[key] <= 20
    
    def test_stub_rubric_sums_to_score(self):
        """Rubric values should sum to fit_score."""
        result = get_stub_analysis()
        
        rubric_sum = sum(result['rubric'].values())
        assert rubric_sum == result['fit_score']

