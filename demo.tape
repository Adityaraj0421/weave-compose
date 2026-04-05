# Run with: vhs demo.tape

Output demo.gif

Set Shell "bash"
Set FontSize 14
Set Width 120
Set Height 30
Set Theme "Dracula"
Set Padding 20

# Activate the virtual environment
Type "source .venv/bin/activate"
Enter
Sleep 1s

# Step 1: Load skills from Claude Code fixtures
Type "weave load ./tests/fixtures/claude_code"
Enter
Sleep 4s

# Step 2: Query for a design task
Type `weave query "design a button component"`
Enter
Sleep 4s

# Step 3: Query for a backend task with score explanation
Type `weave query "write a database migration" --explain`
Enter
Sleep 4s

# Step 4: List all loaded skills
Type "weave list"
Enter
Sleep 2s

# Step 5: Show registry status and session info
Type "weave status"
Enter
Sleep 2s

Sleep 1s
