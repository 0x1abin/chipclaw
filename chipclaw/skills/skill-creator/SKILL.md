---
name: skill-creator
description: Create or update ChipClaw Skills for ESP32-S3. Use when designing, structuring, or documenting skills that provide hardware control workflows, peripheral API references, or embedded system patterns.
---

# Skill Creator

This skill provides guidance for creating effective skills in ChipClaw.

## About Skills

Skills are modular, self-contained packages that extend the agent's capabilities by providing specialized knowledge, workflows, and reference material. In ChipClaw's embedded context, skills serve as "onboarding guides" for ESP32-S3 hardware control, MicroPython peripheral APIs, and domain-specific embedded workflows.

### What Skills Provide

1. **Hardware workflows** - Multi-step procedures for controlling peripherals (sensors, actuators, displays)
2. **API references** - MicroPython peripheral API usage patterns (SPI, I2C, UART, Timer, PWM, etc.)
3. **Domain expertise** - Project-specific hardware configurations, pin assignments, device protocols
4. **Code patterns** - Reusable MicroPython code snippets for common embedded tasks

## Core Principles

### Concise is Key

The context window is a public good shared between system prompt, conversation history, skill metadata, and the user request. ESP32-S3 has limited resources, so context efficiency matters even more.

**Default assumption: the agent is already smart.** Only add context the agent doesn't have. Challenge each piece of information: "Does the agent really need this?" and "Does this justify its token cost?"

Prefer concise examples over verbose explanations.

### Embedded-Specific Constraints

ChipClaw runs on ESP32-S3 with these constraints:

- **No shell/subprocess**: All code runs via `exec_micropython` (exec/eval) or by creating `.py` files with `write_file` and importing them
- **Flash storage limits**: Skills stored on 16MB Flash; keep total size reasonable
- **MicroPython APIs**: Use `machine`, `neopixel`, `dht`, `onewire`, etc., not CPython libraries
- **Hardware access**: Skills often involve GPIO, I2C, SPI, UART, ADC, PWM operations

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility:

**High freedom (text-based instructions)**: Use when multiple approaches are valid or context-dependent decisions are needed.

**Medium freedom (code patterns with parameters)**: Use when a preferred pattern exists but configuration varies (pin assignments, I2C addresses, timing parameters).

**Low freedom (specific code snippets)**: Use when operations are fragile and error-prone, or a specific sequence must be followed (peripheral initialization, protocol timing).

### Anatomy of a Skill

Every skill consists of a single required SKILL.md file:

```
skill-name/
└── SKILL.md (required)
    ├── YAML frontmatter metadata (required)
    │   ├── name: (required)
    │   ├── description: (required)
    │   └── load: (optional, "always" or default)
    └── Markdown instructions (required)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name`, `description`, and optionally `load` fields. The `name` and `description` are the primary triggering mechanism - they determine when the skill gets loaded. Be clear and comprehensive.
- **Body** (Markdown): Instructions, API references, and code patterns. Only loaded AFTER the skill triggers.

#### Simplified Structure for Embedded

Unlike nanobot, ChipClaw skills do NOT include:

- **scripts/** directory - MicroPython code is embedded directly in SKILL.md or created via `write_file` + `exec_micropython`
- **references/** directory - All content goes in SKILL.md since skills are smaller in scope
- **assets/** directory - Template files not typical in embedded context

This simplification reflects ChipClaw's embedded nature: skills are focused API references and workflow guides, not large multi-file packages.

## Skill Creation Process

Skill creation involves these steps:

1. Understand the skill with concrete examples
2. Design the skill structure and content
3. Create the skill directory and SKILL.md
4. Write frontmatter and body content
5. Test the skill
6. Iterate based on usage

Follow these steps in order, skipping only if clearly not applicable.

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize titles to hyphen-case (e.g., "Servo Control" -> `servo-control`)
- Keep names under 64 characters
- Prefer short, descriptive phrases (e.g., `i2c-sensors`, `neopixel-control`, `motor-driver`)
- Name the skill folder exactly after the skill name

### Step 1: Understanding the Skill with Concrete Examples

To create an effective skill, clearly understand how it will be used. Consider:

- "What hardware functionality should this skill support?"
- "What are typical user queries that should trigger this skill?"
- "Can you give examples of workflows this skill would guide?"

Example questions for an `oled-display` skill:

- "Will users need to initialize displays, draw text, graphics, or both?"
- "Should this cover SPI OLEDs, I2C OLEDs, or both?"
- "What would trigger this skill? 'Show text on screen', 'Draw a circle on OLED'?"

### Step 2: Design the Skill Structure

Analyze concrete examples to determine what belongs in the skill:

Example: For a `servo-motor` skill handling queries like "Move servo to 90 degrees":

1. Servo control requires PWM setup with specific frequency (50Hz) and duty cycle mapping
2. The SKILL.md should include:
   - PWM initialization pattern for servos
   - Angle-to-duty cycle conversion formula
   - Pin compatibility notes
   - Example code snippets

Example: For a `temp-sensor` skill handling "Read DHT22 sensor":

1. DHT sensors require specific MicroPython modules and timing
2. The SKILL.md should include:
   - Import statements (`import dht`)
   - Initialization patterns for DHT11 and DHT22
   - Reading temperature and humidity
   - Error handling for failed reads

### Step 3: Create the Skill Directory

Create the skill directory structure:

```bash
mkdir -p chipclaw/skills/<skill-name>
```

Or for user skills:

```bash
mkdir -p workspace/skills/<skill-name>
```

Built-in skills go in `chipclaw/skills/`, user skills in `workspace/skills/`. User skills override built-in skills with the same name.

### Step 4: Write SKILL.md

#### Frontmatter

Write the YAML frontmatter with required fields:

```yaml
---
name: skill-name
description: Brief description of what the skill does and when to use it. Include triggers and use cases.
load: always
---
```

- `name`: The skill name (must match directory name)
- `description`: Primary triggering mechanism. Include:
  - What the skill does
  - Specific triggers/contexts for when to use it
  - Hardware or API scope
  - Example: "MicroPython peripheral API reference for ESP32-S3 (SPI, UART, Timer, NeoPixel, DHT, OneWire, etc.)"
- `load`: Optional. Set to `always` if the skill should be loaded in every agent context (like `peripheral_api`). Omit for on-demand skills.

Do not include any other fields in frontmatter.

#### Body Content

Write instructions using imperative/infinitive form. Structure the body with:

1. **Overview** - Brief introduction to the skill's purpose
2. **Execution Patterns** - How to use `exec_micropython` and `write_file` for the hardware operations
3. **API References** - Code snippets for relevant MicroPython APIs
4. **Common Use Cases** - Practical examples
5. **Pin References** - GPIO pin assignments, constraints
6. **Safety Notes** - Hardware precautions, limitations

**Example structure for a peripheral skill:**

```markdown
# Skill Title

Brief overview of what this skill covers.

## Execution Patterns

### Pattern 1: Direct exec/eval
Show how to use exec_micropython for simple operations.

### Pattern 2: Create .py file and import
Show how to use write_file + exec_micropython for complex code.

## API Reference

### Feature 1
Code snippet with explanation.

### Feature 2
Code snippet with explanation.

## Common Use Cases

### Use Case 1
Practical example.

## Pin Reference

List of relevant GPIO pins and their functions.

## Safety Notes

Hardware precautions and constraints.
```

**Guidelines:**

- Use code blocks with proper syntax highlighting (```python)
- Include actual runnable MicroPython code, not pseudocode
- Show both simple and complex patterns
- Document pin numbers, addresses, timing requirements
- Note hardware constraints (current limits, voltage levels, etc.)
- Keep examples focused on ESP32-S3 specifics

### Step 5: Test the Skill

Test the skill by:

1. **Load verification**: Verify the skill loads correctly:

```python
from chipclaw.agent.skills import SkillsManager
sm = SkillsManager('/workspace')
skill = sm.load_skill('skill-name')
print(skill)
```

2. **Frontmatter parsing**: Ensure frontmatter fields are correct:

```python
print(skill['frontmatter'])
# Should show: {'name': 'skill-name', 'description': '...', 'load': 'always'}
```

3. **Content verification**: Check that the body content is complete:

```python
print(skill['content'][:500])  # First 500 chars
```

4. **Code validation**: If the skill includes code snippets, test them on actual hardware or in MicroPython REPL

### Step 6: Iterate Based on Usage

After deploying the skill, users may request improvements:

**Iteration workflow:**

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Identify what needs updating in SKILL.md
4. Update the content
5. Test again

Common iteration needs:

- Add missing API patterns
- Clarify confusing instructions
- Add more examples for common cases
- Update pin references for specific hardware configurations
- Add error handling patterns

## Progressive Disclosure for Skills

Skills use a two-level loading system:

1. **Metadata (name + description)** - Always in context for skill selection (~100 words)
2. **SKILL.md body** - Loaded when skill triggers (<1000 lines)

Keep SKILL.md body focused and under 500 lines when possible. If a skill grows large, consider splitting into multiple focused skills.

**Example split:**

Instead of one massive `sensors` skill, create:

- `i2c-sensors` - I2C sensor patterns (BME280, MPU6050, etc.)
- `spi-sensors` - SPI sensor patterns (MAX6675, etc.)
- `dht-sensors` - DHT11/DHT22 specific
- `onewire-sensors` - DS18B20 and OneWire devices

This allows the agent to load only relevant content.

## Skill Examples

### Peripheral API Skill

The built-in `peripheral_api` skill demonstrates best practices:

- Clear frontmatter with `load: always`
- Execution patterns using `exec_micropython` and `write_file`
- Multiple API sections (SPI, UART, Timer, NeoPixel, etc.)
- Runnable code snippets
- Pin references and safety notes

See: `chipclaw/skills/peripheral_api/SKILL.md`

### Hardware Control Skill

The `hardware_control` skill shows a user skill pattern:

- Focused on GPIO, I2C, PWM, ADC
- JSON tool call examples
- Common use cases section
- Self-programming patterns

See: `workspace/skills/hardware/SKILL.md`

## What to NOT Include in a Skill

Skills should be lean and focused. Do NOT create:

- README.md files
- Installation guides
- Testing procedures
- Changelogs
- User-facing documentation

Skills are for the AI agent, not human developers. Keep them focused on the task at hand.

## ESP32-S3 Specific Notes

When creating skills for ChipClaw:

1. **Use MicroPython APIs**: `machine`, `neopixel`, `dht`, `onewire`, `ds18x20`, `network`, `ubluetooth`, etc.
2. **No subprocess/shell**: Use `exec_micropython` or `write_file` + import pattern
3. **Memory constraints**: Consider `gc.collect()` for memory-intensive operations
4. **Hardware specifics**: Document ESP32-S3 pin capabilities (ADC pins, UART IDs, etc.)
5. **Flash filesystem**: All files stored on Flash; use `/` as root path
6. **Async patterns**: Use `uasyncio` for concurrent operations, not threads

## Conclusion

Effective skills transform ChipClaw from a general-purpose agent into a specialized embedded systems expert. Keep skills concise, focused, and rich with runnable MicroPython examples.
