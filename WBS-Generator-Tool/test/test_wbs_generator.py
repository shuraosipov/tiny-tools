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
    # Update mock responses to handle AI-related prompts
    mock_confirm.side_effect = [True, True, True, False]  # Start, Save, Preview, AI enrichment
    
    with patch.object(wbs, 'collect_project_data'), \
         patch.object(wbs, 'collect_project_details'), \
         patch.object(wbs, 'save_to_file'), \
         patch.object(wbs, 'generate_wbs_markdown') as mock_generate:
        
        mock_generate.return_value = "# Test WBS"
        wbs.project_info = {"name": "Test Project"}
        
        wbs.run()
        
        mock_generate.assert_called_once()
        assert mock_console_print.call_count >= 3

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
        mock_progress.update.assert_has_calls([
            call(mock_task, advance=1, description="Collecting Risks"),
            call(mock_task, advance=1, description="Collecting Resources"),
            call(mock_task, advance=1)
        ])

@patch('openai.OpenAI')
def test_generate_wbs_markdown(mock_openai, wbs):
    """Test markdown generation"""
    # Setup mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="""
| Task ID | Task Name | Description | Duration | Start Date | End Date |
|---------|-----------|-------------|----------|------------|----------|
| 1.0 | Project Initiation | Initial setup | 5 | 2024-01-01 | 2024-01-06 |
| 2.0 | Deliverable 1 | Description 1 | 2 | 2024-01-07 | 2024-01-21 |
| 2.1 | Subtask 1 | Subtask description | 1 | 2024-01-07 | 2024-01-14 |
"""))]
    mock_openai.return_value.chat.completions.create.return_value = mock_completion
    
    # Setup complete test data with required start_date
    wbs.project_info = {
        "name": "Test Project",
        "description": "Test Description",
        "start_date": "2024-01-01",
        "sponsor": "Test Sponsor",
        "manager": "Test Manager",
        "budget": "1000"
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
    
    # Set OpenAI client
    wbs.openai_client = mock_openai.return_value

    markdown = wbs.generate_wbs_markdown()

    # Verify basic structure and content
    assert "# Work Breakdown Structure: Test Project" in markdown
    assert "## Project Information" in markdown
    assert "## Requirements and Constraints" in markdown
    assert "### Requirements" in markdown
    assert "- Requirement 1" in markdown

    # Verify table structure with known mock output
    assert "| Task ID | Task Name |" in markdown
    assert "| 1.0 | Project Initiation |" in markdown
    assert "| 2.0 | Deliverable 1 |" in markdown
    assert "| 2.1 | Subtask 1 |" in markdown

def test_generate_basic_wbs_table(wbs):
    """Test basic WBS table generation"""
    # Setup test data
    wbs.project_info = {
        "name": "Test Project",
        "description": "Test Description",
        "start_date": "2024-01-01"
    }
    wbs.deliverables = [{
        "name": "Deliverable 1",
        "description": "Description 1",
        "duration": "2",
        "dependencies": "",
        "subtasks": ["Subtask 1"]
    }]
    
    table = wbs.generate_basic_wbs_table()
    
    # Verify table structure
    assert "| Task ID | Task Name | Description |" in table
    assert "| 1.0 | Project Initialization |" in table
    assert "| 2.0 | Deliverable 1 |" in table
    assert "| 2.1 | Subtask 1 |" in table

@patch('openai.OpenAI')
def test_generate_wbs_table_with_ai(mock_openai, wbs):
    """Test WBS table generation with AI"""
    # Setup mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test AI Response"))]
    mock_openai.return_value.chat.completions.create.return_value = mock_completion
    
    # Setup test data
    wbs.project_info = {
        "name": "Test Project",
        "description": "Test Description",
        "start_date": "2024-01-01"
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
    
    # Set OpenAI client
    wbs.openai_client = mock_openai.return_value
    
    table = wbs.generate_wbs_table()
    
    # Verify AI was called with correct prompt
    assert mock_openai.return_value.chat.completions.create.called
    assert table == "Test AI Response"

@patch('openai.OpenAI')
def test_enrich_wbs_with_ai(mock_openai, wbs):
    """Test WBS enrichment with AI"""
    # Setup mock OpenAI response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="AI Analysis"))]
    mock_openai.return_value.chat.completions.create.return_value = mock_completion
    
    # Set OpenAI client
    wbs.openai_client = mock_openai.return_value
    
    result = wbs.enrich_wbs_with_ai("Original WBS Content")
    
    # Verify AI was called and content was enriched
    assert mock_openai.return_value.chat.completions.create.called
    assert "Original WBS Content" in result
    assert "AI Analysis" in result
    assert "## AI-Enhanced Project Analysis" in result