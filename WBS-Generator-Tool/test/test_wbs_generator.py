import pytest
from unittest.mock import patch, mock_open, MagicMock, call
from wbs_generator import WBSGenerator
import datetime
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress

@pytest.fixture
def wbs():
    return WBSGenerator()

def test_initialization(wbs):
    """Test if WBSGenerator initializes with correct attributes"""
    assert hasattr(wbs, 'project_info')
    assert isinstance(wbs.project_info, dict)
    assert isinstance(wbs.requirements, list)
    assert isinstance(wbs.constraints, list)
    assert isinstance(wbs.deliverables, list)
    assert isinstance(wbs.risks, list)
    assert isinstance(wbs.resources, list)
    assert hasattr(wbs, 'console')
    assert isinstance(wbs.console, Console)

@patch('rich.prompt.Prompt.ask')
def test_get_input_required(mock_ask, wbs):
    """Test get_input with required input"""
    mock_ask.return_value = "test input"
    result = wbs.get_input("Test prompt", required=True)
    assert result == "test input"
    mock_ask.assert_called_once_with("[cyan]Test prompt[/cyan]")

@patch('rich.prompt.Prompt.ask')
def test_get_input_required_empty(mock_ask, wbs):
    """Test get_input with empty required input"""
    mock_ask.side_effect = ["", "valid input"]
    result = wbs.get_input("Test prompt", required=True)
    assert result == "valid input"
    assert mock_ask.call_count == 2

@patch('builtins.input')
def test_get_multiline_input(mock_input, wbs):
    """Test get_multiline_input method"""
    mock_input.side_effect = ["line 1", "line 2", ""]
    result = wbs.get_multiline_input("Test prompt")
    assert result == ["line 1", "line 2"]

@patch('rich.prompt.Prompt.ask')
def test_collect_project_info(mock_ask, wbs):
    """Test project info collection"""
    mock_inputs = [
        "Test Project",          # name
        "Test Description",      # description
        "2024-01-01",           # start_date
        "Test Sponsor",          # sponsor
        "Test Manager",          # manager
        "1000"                  # budget
    ]
    mock_ask.side_effect = mock_inputs
    
    wbs.collect_project_info()
    
    assert wbs.project_info["name"] == "Test Project"
    assert wbs.project_info["description"] == "Test Description"
    assert wbs.project_info["start_date"] == "2024-01-01"
    assert wbs.project_info["sponsor"] == "Test Sponsor"
    assert wbs.project_info["manager"] == "Test Manager"
    assert wbs.project_info["budget"] == "1000"

@patch('rich.console.Console.print')
def test_display_section_header(mock_console_print, wbs):
    """Test section header display"""
    wbs.display_section_header("Test Section")
    mock_console_print.assert_called_once()

def test_display_summary(wbs):
    """Test summary table generation"""
    wbs.requirements = ["req1", "req2"]
    wbs.constraints = ["const1"]
    wbs.deliverables = [{"name": "del1"}]
    wbs.risks = [{"description": "risk1"}, {"description": "risk2"}]
    wbs.resources = [{"role": "res1"}]
    
    with patch('rich.console.Console.print') as mock_print:
        wbs.display_summary()
        mock_print.assert_called_once()

@patch('rich.prompt.Confirm.ask')
@patch('rich.console.Console.print')
def test_run_with_save_and_preview(mock_console_print, mock_confirm, wbs):
    """Test run method with save and preview options"""
    mock_confirm.side_effect = [True, True, True]  # Start: Yes, Save: Yes, Preview: Yes
    
    with patch.object(wbs, 'collect_project_data'), \
         patch.object(wbs, 'collect_project_details'), \
         patch.object(wbs, 'save_to_file'), \
         patch.object(wbs, 'generate_wbs_markdown') as mock_generate:
        
        mock_generate.return_value = "# Test WBS"
        wbs.project_info = {"name": "Test Project"}
        
        wbs.run()
        
        mock_generate.assert_called_once()
        assert mock_console_print.call_count >= 3  # Welcome panel, save message, and preview

@patch('rich.console.Console.print')
@patch('rich.prompt.Confirm.ask', return_value=True)
def test_keyboard_interrupt_handling(mock_confirm, mock_console_print, wbs):
    """Test handling of keyboard interrupts"""
    with patch.object(wbs, 'collect_project_data', side_effect=KeyboardInterrupt):
        wbs.run()
        mock_console_print.assert_called_with("\n\n[yellow]Process cancelled by user.[/yellow]")

@patch("builtins.open", new_callable=mock_open)
def test_save_to_file(mock_file, wbs):
    """Test file saving functionality"""
    content = "Test content"
    filename = "test.md"
    
    wbs.save_to_file(content, filename)
    
    mock_file.assert_called_once_with(filename, 'w')
    mock_file().write.assert_called_once_with(content)

@patch('builtins.input')
def test_collect_deliverable(mock_input, wbs):
    """Test deliverable collection"""
    mock_input.side_effect = [
        "Deliverable 1",  # name
        "Description 1",  # description
        "2",             # duration
        "Dep 1",        # dependencies
        "Subtask 1",    # subtask
        ""              # empty line to end subtasks
    ]
    
    deliverable = wbs.collect_deliverable()
    
    assert deliverable["name"] == "Deliverable 1"
    assert deliverable["description"] == "Description 1"
    assert deliverable["duration"] == "2"
    assert deliverable["dependencies"] == "Dep 1"
    assert "Subtask 1" in deliverable["subtasks"]

@patch('wbs_generator.Progress')  # Change the import path to match where Progress is used
def test_collect_project_data_with_progress(mock_progress_class, wbs):
    """Test project data collection with progress"""
    # Create mock progress instance
    mock_progress = MagicMock()
    mock_task = MagicMock()
    
    # Set up the mock progress instance
    mock_progress.add_task.return_value = mock_task
    
    # Set up the Progress class mock to return our mock instance
    mock_progress_class.return_value = mock_progress
    
    # Mock the context manager methods
    mock_progress.__enter__.return_value = mock_progress
    mock_progress.__exit__.return_value = None
    
    # Mock the collection methods to prevent actual collection
    with patch.object(wbs, 'collect_project_info'), \
         patch.object(wbs, 'collect_requirements'), \
         patch.object(wbs, 'collect_constraints'):
        
        wbs.collect_project_data()
        
        # Verify Progress usage
        mock_progress.add_task.assert_called_once_with("Collecting Project Data", total=3)
        assert mock_progress.update.call_count == 3
        
        # Verify the update calls happened with correct parameters
        mock_progress.update.assert_has_calls([
            call(mock_task, advance=1, description="Collecting Requirements"),
            call(mock_task, advance=1, description="Collecting Constraints"),
            call(mock_task, advance=1)
        ])

@patch('wbs_generator.Progress')  # Change the import path to match where Progress is used
def test_collect_project_details_with_progress(mock_progress_class, wbs):
    """Test project details collection with progress"""
    # Create mock progress instance
    mock_progress = MagicMock()
    mock_task = MagicMock()
    
    # Set up the mock progress instance
    mock_progress.add_task.return_value = mock_task
    
    # Set up the Progress class mock to return our mock instance
    mock_progress_class.return_value = mock_progress
    
    # Mock the context manager methods
    mock_progress.__enter__.return_value = mock_progress
    mock_progress.__exit__.return_value = None
    
    # Mock the collection methods to prevent actual collection
    with patch.object(wbs, 'collect_deliverables'), \
         patch.object(wbs, 'collect_risks'), \
         patch.object(wbs, 'collect_resources'):
        
        wbs.collect_project_details()
        
        # Verify Progress usage
        mock_progress.add_task.assert_called_once_with("Collecting Project Details", total=3)
        assert mock_progress.update.call_count == 3
        
        # Verify the update calls happened with correct parameters
        mock_progress.update.assert_has_calls([
            call(mock_task, advance=1, description="Collecting Risks"),
            call(mock_task, advance=1, description="Collecting Resources"),
            call(mock_task, advance=1)
        ])

def test_generate_wbs_markdown(wbs):
    """Test markdown generation"""
    wbs.project_info = {
        "name": "Test Project",
        "description": "Test Description"
    }
    wbs.requirements = ["Requirement 1"]
    wbs.constraints = ["Constraint 1"]
    wbs.deliverables = [{
        "name": "Deliverable 1",
        "description": "Description 1",
        "duration": "2",
        "dependencies": "",
        "subtasks": ["Subtask 1"]
    }]
    
    markdown = wbs.generate_wbs_markdown()
    
    assert "# Work Breakdown Structure: Test Project" in markdown
    assert "## Requirements" in markdown
    assert "1. Requirement 1" in markdown