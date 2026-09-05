# September 6, 2026 youth Sunday School

Entry: `/cfm906-youth.html`. A separate, teacher-led lesson for 22 twelve-year-olds. No student accounts, submitted answers, or persistent student data. The class uses the projected page, nearby pairs, and paper.

## Sources and suggested pauses

The [official September 6 instructions](https://www.churchofjesuschrist.org/study/manual/changes-to-the-sunday-class-meeting-schedule-instruction-2026/youth-and-adult-sunday-instruction-materials?lang=eng) assign both complete videos and discussion after each. The page includes both videos without editing them. The suggested checkpoints below are this lesson's teaching aids, not additional Church instructions.

| Video | Page label | Checkpoint | Caption boundary | Activity |
| --- | --- | --- | --- | --- |
| The Sabbath and Sacrament Meeting | 3:08 | 188.0 seconds | Sentence on forgiveness ends at 3:07.851; next begins at 3:09.386 | 30-second written thought, box 1 |
| The Sabbath and Sacrament Meeting | 7:21 | 440.5 seconds | Sentence ends at 7:20.236; next begins at 7:21.004 | 30-second choice, box 2 |
| Sunday School | 2:33 | 153.2 seconds | Partner demonstration ends at 2:32.916; next begins at 2:33.984 | 45 seconds for both partners, box 3 |

Checkpoint labels round to the nearest second. English captions are reused from `../cfm906/sabbath-en.vtt` and `../cfm906/sunday-school-en.vtt`. Timing was checked against those supplied captions. A checkpoint fires once during normal playback. Seeking past it or disabling guided pauses skips it. Teacher previews do not consume checkpoints or resume playback. Timers never resume a video automatically.

The plan totals 21:30, leaving 3:30 for arrivals and transitions within the 25-minute class. The Psalm 119:105 activity is optional and comes from [this week's Come, Follow Me lesson](https://www.churchofjesuschrist.org/study/manual/come-follow-me-for-home-and-church-old-testament-2026/36?lang=eng). Scripture uses the King James Version.

## Media and design

Reuses the existing lesson's `reverential-return.jpg` and `family-scripture-study.jpg`, with permission confirmed by the teacher. See `../cfm906/images/README.md` for original sources and credits. Adult lesson files are unchanged. The palette uses the [Core OTW colors](https://outsidetheworld.com/palette.html) on a light background.

## Handout and checks

`sunday-notes.pdf`: one US Letter page, two identical half-sheet cards. Print 11 copies, single-sided, actual size, and cut at the center line for 22 students.

- Rebuild PDF: `python3 tools/build_cfm906_youth_handout.py` (requires ReportLab).
- Interaction checks: `node tools/test_cfm906_youth.mjs` (also requires Python 3). This uses a small simulated DOM to check navigation, prompts, video timing, and timers; it is not a browser rendering test.
- Local asset audit: `python3 tools/audit_public_site.py --strict`.

The PDF was rendered and visually checked. The video and page controls still benefit from a sound check on the classroom computer before class.
