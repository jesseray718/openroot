# FLASH DRIVE PREPARATION INSTRUCTIONS

## Step 1: Format the 128GB Flash Drive

### On Windows:
1. Insert the 128GB flash drive
2. Open File Explorer > This PC
3. Right-click the flash drive > Format
4. Select FAT32 (for maximum compatibility)
5. Quick Format: Yes
6. Start

### On Linux:
```bash
sudo mkfs.vfat -F32 /dev/sdX1
```

## Step 2: Create Directory Structure

Create these folders on the flash drive:
- `OMBU_CORE/` - Main knowledge base
- `TOOLS/` - Utilities
- `BOOT/` - Bootable images
- `DELL_3040/` - Specific hardware files

## Step 3: Copy the Ink Code

Copy these files to `OMBU_CORE/`:
- `HUMAN_CONTINUITY_MASTER_v1.0.txt` (the main record)
- `RETRIEVAL_PROTOCOL.md`
- `INK_CODE_MANIFESTO.md`
- `PUBLIC_TEASER.md`

## Step 4: Prepare Ubuntu Image

Download Ubuntu 24.04 LTS ISO:
- From: https://ubuntu.com/download/desktop
- Save to: `BOOT/ubuntu-24.04-desktop-amd64.iso`

## Step 5: Dell Optiplex 3040 Files

Create `DELL_3040/` with:
- Drivers (from Dell support site)
- BIOS updates
- Hardware specs

## Step 6: Verify All Files

Check that all files are present and readable:
```bash
# On Linux
find /media/flash_drive -type f -exec file {} \;

# On Windows
Open each folder and verify files

## Step 7: Eject Safely

Always eject the flash drive properly to avoid corruption.
