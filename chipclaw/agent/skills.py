"""
ChipClaw Skills Loader
Loads and manages skill documents with frontmatter parsing
"""
import os
from ..utils import file_exists


class SkillsManager:
    """Skills management system"""
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.user_skills_dir = workspace + "/skills"
        # Built-in skills bundled with chipclaw package
        self.builtin_skills_dir = self._find_builtin_skills_dir()
    
    def _find_builtin_skills_dir(self):
        """
        Locate the built-in skills directory relative to the chipclaw package.
        Works on both ESP32 (absolute paths) and CPython (relative paths).
        
        Returns:
            Path string to builtin skills dir, or None if not found
        """
        # Determine path relative to this file: chipclaw/agent/skills.py
        # Built-in skills are at: chipclaw/skills/
        try:
            # Go up from chipclaw/agent/ to chipclaw/, then into skills/
            agent_dir = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
            package_dir = agent_dir.rsplit('/', 1)[0] if '/' in agent_dir else '.'
            builtin_dir = package_dir + "/skills"
            if file_exists(builtin_dir):
                return builtin_dir
        except Exception:
            pass
        return None
    
    def _list_skills_in_dir(self, skills_dir):
        """
        List skill names in a given directory.
        
        Args:
            skills_dir: Path to skills directory
        
        Returns:
            List of skill names (directory names)
        """
        skills = []
        if skills_dir and file_exists(skills_dir):
            try:
                for item in os.listdir(skills_dir):
                    skill_path = f"{skills_dir}/{item}"
                    skill_file = f"{skill_path}/SKILL.md"
                    if file_exists(skill_file):
                        skills.append(item)
            except Exception as e:
                print(f"Error listing skills in {skills_dir}: {e}")
        return skills
    
    def list_skills(self):
        """
        List all available skills (user + builtin).
        User skills override builtin skills with the same name.
        
        Returns:
            List of skill names (directory names)
        """
        seen = set()
        skills = []
        
        # User skills (take priority)
        for name in self._list_skills_in_dir(self.user_skills_dir):
            if name not in seen:
                seen.add(name)
                skills.append(name)
        
        # Built-in skills (only add if not overridden by user)
        for name in self._list_skills_in_dir(self.builtin_skills_dir):
            if name not in seen:
                seen.add(name)
                skills.append(name)
        
        return skills
    
    def load_skill(self, name):
        """
        Load skill markdown + frontmatter.
        Looks in user skills first, then builtin skills.
        
        Args:
            name: Skill name (directory name)
        
        Returns:
            Dict with 'frontmatter' (dict) and 'content' (str)
            Returns None if skill not found
        """
        # Try user skills first, then builtin
        skill_path = f"{self.user_skills_dir}/{name}/SKILL.md"
        
        if not file_exists(skill_path):
            # Fall back to builtin skills
            if self.builtin_skills_dir:
                skill_path = f"{self.builtin_skills_dir}/{name}/SKILL.md"
            if not file_exists(skill_path):
                return None
        
        try:
            with open(skill_path, 'r') as f:
                content = f.read()
            
            frontmatter, body = self._parse_frontmatter(content)
            
            return {
                'name': name,
                'frontmatter': frontmatter,
                'content': body
            }
        except Exception as e:
            print(f"Error loading skill '{name}': {e}")
            return None
    
    def _parse_frontmatter(self, content):
        """
        Parse frontmatter from markdown content
        Simple parser for --- blocks with key: value pairs
        
        Args:
            content: Full markdown content
        
        Returns:
            Tuple of (frontmatter_dict, body_content)
        """
        frontmatter = {}
        body = content
        
        # Check if content starts with ---
        if content.startswith('---\n') or content.startswith('---\r\n'):
            # Find end of frontmatter
            lines = content.split('\n')
            end_idx = -1
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    end_idx = i
                    break
            
            if end_idx > 0:
                # Parse frontmatter lines
                for line in lines[1:end_idx]:
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
                
                # Body is everything after frontmatter
                body = '\n'.join(lines[end_idx + 1:])
        
        return frontmatter, body
    
    def get_always_skills(self):
        """
        Get skills with 'load: always' in frontmatter
        
        Returns:
            List of skill dicts
        """
        always_skills = []
        
        for skill_name in self.list_skills():
            skill = self.load_skill(skill_name)
            if skill and skill['frontmatter'].get('load') == 'always':
                always_skills.append(skill)
        
        return always_skills
    
    def load_skills_for_context(self, names):
        """
        Load multiple skills for context
        
        Args:
            names: List of skill names
        
        Returns:
            List of skill dicts
        """
        skills = []
        for name in names:
            skill = self.load_skill(name)
            if skill:
                skills.append(skill)
        return skills
    
    def build_skills_summary(self):
        """
        Generate available skills list for context
        
        Returns:
            Formatted string listing available skills
        """
        all_skills = self.list_skills()
        
        if not all_skills:
            return "No skills available."
        
        lines = ["## Available Skills"]
        for skill_name in all_skills:
            skill = self.load_skill(skill_name)
            if skill:
                description = skill['frontmatter'].get('description', 'No description')
                lines.append(f"- **{skill_name}**: {description}")
        
        return '\n'.join(lines)
