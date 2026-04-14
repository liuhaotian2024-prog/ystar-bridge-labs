## Mission 2: L6 Lesson Capture Auto-Trigger
Engineer: eng-platform (Ryan Park)
Priority: P0
L-label: L6 (Learning Loop - organizational knowledge accumulation)

Gap: Learning loop has no auto-capture — relies on manual Board/CEO extraction.

Acceptance Criteria:
- [ ] Create `scripts/lesson_capture_trigger.py`
- [ ] Detect Board frustration markers: FORGET_GUARD spike, repeated violations, Board CROBA override
- [ ] Emit `LESSON_CAPTURE_DUE` event to CIEU
- [ ] Write stub template to `knowledge/ceo/lessons/{timestamp}-lesson-stub.md` with context
- [ ] Add cron entry (example, Board installs): `*/20 * * * * python3 scripts/lesson_capture_trigger.py`
- [ ] Test with mock FORGET_GUARD spike, verify stub written
- [ ] Commit, report hash + L6 label

Files in scope: scripts/lesson_capture_trigger.py, knowledge/ceo/lessons/
