# Autonomous Voice Scheduler — spec v0.1 (STUB; provider choice = OPEN question)
Flow: inbound call -> PBX (Twilio/Telnyx self-hosted Asterisk both viable) -> Whisper STT
-> openroot-coder intent extraction -> sqlite calendar -> TTS confirm -> SMS reminder.
Booking API: POST /book {name, service(e-waste pickup|dropoff|data-destruction), addr, slot}.
Calendar: lever.db bookings table + .ics export to phone.
Human-in-loop: OFF by default after 10 graded transcripts; rc_circuit scores each call.
Prereq: phone line (prepaid-number task, already queued at 0.15).
