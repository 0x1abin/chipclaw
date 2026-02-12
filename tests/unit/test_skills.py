"""
Unit tests for chipclaw.agent.skills module
Tests builtin skills loading and user/builtin priority
"""
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chipclaw.agent.skills import SkillsManager


def test_skills_manager_creation():
    """Test SkillsManager initialization"""
    sm = SkillsManager("/workspace")
    assert sm.workspace == "/workspace"
    assert sm.user_skills_dir == "/workspace/skills"


def test_builtin_skills_dir_found():
    """Test that builtin skills directory is discovered"""
    sm = SkillsManager("/workspace")
    # The builtin_skills_dir should be found (chipclaw/skills/ exists)
    assert sm.builtin_skills_dir is not None
    assert sm.builtin_skills_dir.endswith("/skills")


def test_builtin_skill_listed():
    """Test that builtin skills appear in list_skills"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Use a workspace with no user skills
        workspace = os.path.join(temp_dir, "workspace")
        os.makedirs(workspace)
        
        sm = SkillsManager(workspace)
        skills = sm.list_skills()
        
        # Should include the builtin peripheral_api skill
        assert "peripheral_api" in skills
    finally:
        shutil.rmtree(temp_dir)


def test_builtin_skill_loaded():
    """Test loading a builtin skill"""
    temp_dir = tempfile.mkdtemp()
    try:
        workspace = os.path.join(temp_dir, "workspace")
        os.makedirs(workspace)
        
        sm = SkillsManager(workspace)
        skill = sm.load_skill("peripheral_api")
        
        assert skill is not None
        assert skill['name'] == "peripheral_api"
        assert skill['frontmatter'].get('name') == "peripheral_api"
        assert skill['frontmatter'].get('load') == "always"
        assert "MicroPython" in skill['content']
    finally:
        shutil.rmtree(temp_dir)


def test_user_skill_overrides_builtin():
    """Test that user skills take priority over builtin skills"""
    temp_dir = tempfile.mkdtemp()
    try:
        workspace = os.path.join(temp_dir, "workspace")
        user_skill_dir = os.path.join(workspace, "skills", "peripheral_api")
        os.makedirs(user_skill_dir)
        
        # Create a user skill that overrides the builtin
        with open(os.path.join(user_skill_dir, "SKILL.md"), 'w') as f:
            f.write("---\nname: peripheral_api\ndescription: User override\nload: always\n---\n\n# User Version\nCustom content\n")
        
        sm = SkillsManager(workspace)
        skill = sm.load_skill("peripheral_api")
        
        assert skill is not None
        assert skill['frontmatter'].get('description') == "User override"
        assert "User Version" in skill['content']
    finally:
        shutil.rmtree(temp_dir)


def test_builtin_always_skills():
    """Test that builtin always-load skills are returned"""
    temp_dir = tempfile.mkdtemp()
    try:
        workspace = os.path.join(temp_dir, "workspace")
        os.makedirs(workspace)
        
        sm = SkillsManager(workspace)
        always = sm.get_always_skills()
        
        # peripheral_api has load: always
        names = [s['name'] for s in always]
        assert "peripheral_api" in names
    finally:
        shutil.rmtree(temp_dir)


def test_skills_summary_includes_builtin():
    """Test that skills summary includes builtin skills"""
    temp_dir = tempfile.mkdtemp()
    try:
        workspace = os.path.join(temp_dir, "workspace")
        os.makedirs(workspace)
        
        sm = SkillsManager(workspace)
        summary = sm.build_skills_summary()
        
        assert "peripheral_api" in summary
        assert "Available Skills" in summary
    finally:
        shutil.rmtree(temp_dir)


def test_parse_frontmatter():
    """Test frontmatter parsing"""
    sm = SkillsManager("/workspace")
    
    content = "---\nname: test\ndescription: A test skill\nload: always\n---\n\n# Test Skill\nBody content\n"
    frontmatter, body = sm._parse_frontmatter(content)
    
    assert frontmatter['name'] == "test"
    assert frontmatter['description'] == "A test skill"
    assert frontmatter['load'] == "always"
    assert "Test Skill" in body


def test_list_skills_in_dir_nonexistent():
    """Test listing skills in non-existent directory"""
    sm = SkillsManager("/workspace")
    skills = sm._list_skills_in_dir("/nonexistent/path")
    assert skills == []


def test_list_skills_in_dir_none():
    """Test listing skills with None directory"""
    sm = SkillsManager("/workspace")
    skills = sm._list_skills_in_dir(None)
    assert skills == []


if __name__ == "__main__":
    from tests import run_tests
    import sys
    run_tests(sys.modules[__name__])
