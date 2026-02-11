"""
ChipClaw Skills Loader
Loads and manages skill documents with frontmatter parsing
"""
import os


class SkillsManager:
    """Skills management system"""
    
    def __init__(self, workspace):
        self.workspace = workspace
        self.user_skills_dir = workspace + "/skills"
        # Could add builtin skills directory later if needed
        self.builtin_skills_dir = None
    
    def list_skills(self):
        """
        List all available skills (user + builtin)
        
        Returns:
            List of skill names (directory names)
        """
        skills = []
        
        # User skills
        if os.path.exists(self.user_skills_dir):
            try:
                for item in os.listdir(self.user_skills_dir):
                    skill_path = f"{self.user_skills_dir}/{item}"
                    skill_file = f"{skill_path}/SKILL.md"
                    if os.path.exists(skill_file):
                        skills.append(item)
            except Exception as e:
                print(f"Error listing user skills: {e}")
        
        return skills
    
    def load_skill(self, name):
        """
        Load skill markdown + frontmatter
        
        Args:
            name: Skill name (directory name)
        
        Returns:
            Dict with 'frontmatter' (dict) and 'content' (str)
            Returns None if skill not found
        """
        # Try user skills first
        skill_path = f"{self.user_skills_dir}/{name}/SKILL.md"
        
        if not os.path.exists(skill_path):
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
