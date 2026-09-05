# Lesson: Executing Huge Commands Without Error on Termux (A15)

## Goal
Run long, multi-line blocks (especially heredocs) reliably on Samsung Galaxy A15 + Termux.

## Proven High-η Method

1. Always use single-quoted terminator:
   cat > file << 'EOF'
   ...content...
   EOF

2. Paste the entire block in one continuous paste. Do not edit mid-paste.

3. After the last line of content, press Enter once, then type the terminator (EOF) on its own line and press Enter again.

4. Immediately verify:
   ls -la file
   wc -l file
   head -n 5 file

5. If the file is missing or truncated:
   - rm the partial file
   - re-paste the full block
   - never try to "fix" a broken heredoc

## Why this works
- Single quotes prevent expansion and most clipboard corruption
- Immediate verification catches silent failures before you move on
- Clean paste + correct terminator is the highest-reliability path on this device

## Anti-patterns (avoid)
- Double-quoted terminator (<< "EOF")
- Trying to edit the pasted text inside Termux
- Assuming success without checking the file exists and has content
- Mixing markdown artifacts from chat into the paste

## Rule
Long blocks are allowed and preferred. The cost of failure is low if you always verify immediately after the command.
