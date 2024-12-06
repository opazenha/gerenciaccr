"""
Tests for the GerenciaCrews class
"""
import pytest
from src.gerencia_ccr.crews.crew import GerenciaCrews
from crewai import Agent, Task

def test_gerencia_crews_initialization():
    """Test GerenciaCrews class initialization."""
    crew = GerenciaCrews()
    assert crew is not None
    assert isinstance(crew.agents_config, dict)
    assert 'reporting_analyst' in crew.agents_config

def test_before_kickoff_hook():
    """Test the before_kickoff hook adds extra data."""
    crew = GerenciaCrews()
    inputs = {}
    result = crew.pull_data_example(inputs)
    assert 'extra_data' in result
    assert result['extra_data'] == "This is extra data"

def test_researcher_agent():
    """Test researcher agent creation."""
    crew = GerenciaCrews()
    agent = crew.researcher()
    assert isinstance(agent, Agent)
    assert agent.verbose is True

def test_reporting_analyst_agent():
    """Test reporting analyst agent creation."""
    crew = GerenciaCrews()
    agent = crew.reporting_analyst()
    assert isinstance(agent, Agent)
    assert agent.verbose is True

def test_research_task():
    """Test research task creation."""
    crew = GerenciaCrews()
    task = crew.research_task()
    assert isinstance(task, Task)

def test_reporting_task():
    """Test reporting task creation."""
    crew = GerenciaCrews()
    task = crew.reporting_task()
    assert isinstance(task, Task)
