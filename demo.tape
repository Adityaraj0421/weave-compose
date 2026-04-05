# Run with: vhs demo.tape

Output demo.gif

Set Shell "bash"
Set FontSize 13
Set Width 1200
Set Height 600
Set Theme "Dracula"
Set Padding 20
Env PATH "/Users/adityaraj0421/weave-compose/.venv/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# Step 1: Load skills from Claude Code fixtures
Type "weave load ./tests/fixtures/claude_code"
Enter
Sleep 6s

# Step 2: Query for a design task
Type `weave query "design a button component"`
Enter
Sleep 6s

# Step 3: Query for a backend task with score explanation
Type `weave query "write a database migration" --explain`
Enter
Sleep 6s

# Step 4: List all loaded skills
Type "weave list"
Enter
Sleep 3s

# Step 5: Show registry status and session info
Type "weave status"
Enter
Sleep 3s

Sleep 1s
