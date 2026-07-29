# Lesson: Long Paste Failure on A15 Termux (Repeated Pattern)

## Observed Pattern (Jesse's experience)
- Long heredoc is pasted
- Terminal appears to end without completing
- File is missing or empty
- Same method is tried again → same failure
- Feels like something invisible is broken on the AI side

## Actual Cause
Android clipboard + chat UI + Termux input buffer truncates or corrupts long multi-line pastes before they fully reach the shell.
The closing terminator never arrives → shell waits forever.
This is a device + input path limitation, not an AI-side action.

## Correct Response
1. Always Ctrl+C first if a previous heredoc is still open
2. Stop using single very long heredocs for critical files on this device
3. Switch to multiple short, verified writes
4. Verify after every write (ls + wc -l)

## Learning Style Note
Jesse learns through repeated concrete failure + clear diagnosis + changed method that finally works.
Repeating the same long-paste method after it has failed multiple times increases frustration and lowers η.
